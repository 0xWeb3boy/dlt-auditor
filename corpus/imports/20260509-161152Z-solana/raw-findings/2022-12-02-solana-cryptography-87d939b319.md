---
case_id: case_20221202_87d939b319
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
source_quality: high
date: 2022-12-02
source_refs:
  - git:87d939b3197ee210acd77575bdf3aa492151bd3c
  - "zk-token-sdk/src/sigma_proofs/pubkey_proof.rs:150"
  - "zk-token-sdk/src/sigma_proofs/pubkey_proof.rs:137"
  - "zk-token-sdk/src/encryption/elgamal.rs:72"
  - "zk-token-sdk/src/encryption/elgamal.rs:264"
bug_class: incorrect-cryptographic-key-derivation
impact_type:
  - cryptographic-integrity
confidence: medium
tags:
  - cryptography
  - elgamal
  - key-derivation
  - zk-proofs
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes inconsistent ElGamal public-key derivation in the zk-token SDK. Before the change, `ElGamalPubkey::new` derived the public key as `secret * H`, while `keygen_with_scalar` used `secret.invert() * H`. After the change, `ElGamalPubkey::new` asserts the scalar is nonzero and uses `s.invert() * H`, and `keygen_with_scalar` delegates to that helper. The accompanying `pubkey_proof.rs` changes add test coverage for derived keypairs; they do not change verifier logic.

## Observed Patch Facts

1. In `zk-token-sdk/src/sigma_proofs/pubkey_proof.rs`, the patch adds `.verify(&keypair.public, &mut verifier_transcript)`.

2. In `zk-token-sdk/src/sigma_proofs/pubkey_proof.rs`, the patch replaces `fn test_pubkey_proof_correctness() {` with `super::*,`.

3. In `zk-token-sdk/src/encryption/elgamal.rs`, the patch replaces `assert!(s != &Scalar::zero());` with `let secret = ElGamalSecretKey(*s);`.

4. In `zk-token-sdk/src/encryption/elgamal.rs`, the patch replaces `ElGamalPubkey(&secret.0 * &(*H))` with `let s = &secret.0;`.

## Project Context

The changed code sits primarily in `zk-token-sdk/src/sigma_proofs`, `zk-token-sdk/src`, `zk-token-sdk/src/encryption`, which anchors the finding in the `cryptography` area of the project. Historical context from `zk-token-sdk/src/sigma_proofs/zero_balance_proof.rs`, `zk-token-sdk/src/sigma_proofs/equality_proof.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `zk-token-sdk/src/sigma_proofs/zero_balance_proof.rs`, `zk-token-sdk/src/sigma_proofs/equality_proof.rs`. The strongest project-level identifiers around this patch are `secret`, `Transcript::new`, `Scalar::zero`, and `test`.

## Before/After Behavior

Before the patch, the canonical helper `ElGamalPubkey::new(secret)` returned `ElGamalPubkey(&secret.0 * &(*H))`, while `keygen_with_scalar(s)` separately asserted `s != Scalar::zero()` and computed `s.invert() * &(*H)`. After the patch, `ElGamalPubkey::new` performs the nonzero assertion and returns `ElGamalPubkey(s.invert() * &(*H))`; `keygen_with_scalar` constructs an `ElGamalSecretKey` and calls `ElGamalPubkey::new(&secret)`. The test change verifies `PubkeySigmaProof` for both random and derived ElGamal keypairs.

# Root Cause

The root cause was inconsistent public-key derivation across ElGamal key construction paths. The canonical helper and scalar-based key generation used different formulas, which could produce keypairs that did not satisfy the expected private/public relation for proof generation and verification.

## Walkthrough

1. `ElGamalPubkey::new` was the canonical helper for deriving a public key from an `ElGamalSecretKey`.

2. Before the patch, that helper computed the public key with scalar multiplication by `H`.

3. `keygen_with_scalar` independently computed the public key with inverse-scalar multiplication by `H` after checking for zero.

4. The patch moves the inverse-scalar formula and zero-scalar assertion into `ElGamalPubkey::new`.

5. `keygen_with_scalar` now delegates public-key derivation to `ElGamalPubkey::new`, removing the duplicate formula.

6. The `pubkey_proof.rs` update adds test coverage showing a derived ElGamal keypair can produce a public-key sigma proof that verifies against its public key.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| zk-token-sdk/src/encryption/elgamal.rs | 72 | ElGamal keypair generation from a supplied scalar now delegates to the canonical public-key derivation routine. |
| zk-token-sdk/src/encryption/elgamal.rs | 264 | Canonical ElGamal public-key derivation now asserts a nonzero secret and computes inverse-scalar times H. |
| zk-token-sdk/src/sigma_proofs/pubkey_proof.rs | 145 | Test coverage verifies pubkey sigma proof correctness for both random and derived ElGamal keypairs. |

## Code Snippets

## Snippet 1

Context: `zk-token-sdk/src/sigma_proofs/pubkey_proof.rs:150` (changes signature or replay validation logic)

Before
```rust
let mut verifier_transcript = Transcript::new(b"test");

        let proof = PubkeySigmaProof::new(&keypair, &mut prover_transcript);
        assert!(proof
```
After
```rust
let mut verifier_transcript = Transcript::new(b"test");

        let proof = PubkeySigmaProof::new(&keypair, &mut prover_transcript);
        assert!(proof
            .verify(&keypair.public, &mut verifier_transcript)
            .is_ok());

        // derived ElGamal keypair
```

## Snippet 2

Context: `zk-token-sdk/src/sigma_proofs/pubkey_proof.rs:137` (changes signature or replay validation logic)

Before
```rust
#[cfg(test)]
mod test {
    use super::*;

    #[test]
    fn test_pubkey_proof_correctness() {
        let keypair = ElGamalKeypair::new_rand();
```
After
```rust
#[cfg(test)]
mod test {
    use {
        super::*,
        solana_sdk::{pubkey::Pubkey, signature::Keypair},
    };

    #[test]
```

## Snippet 3

Context: `zk-token-sdk/src/encryption/elgamal.rs:72` (changes the branch that decides whether execution stops or continues)

Before
```rust
#[allow(non_snake_case)]
    fn keygen_with_scalar(s: &Scalar) -> ElGamalKeypair {
        assert!(s != &Scalar::zero());

        let P = s.invert() * &(*H);

        ElGamalKeypair {
            public: ElGamalPubkey(P),
```
After
```rust
#[allow(non_snake_case)]
    fn keygen_with_scalar(s: &Scalar) -> ElGamalKeypair {
        let secret = ElGamalSecretKey(*s);
        let public = ElGamalPubkey::new(&secret);

        ElGamalKeypair { public, secret }
    }
```

## Snippet 4

Context: `zk-token-sdk/src/encryption/elgamal.rs:264` (changes the branch that decides whether execution stops or continues)

Before
```rust
#[allow(non_snake_case)]
    pub fn new(secret: &ElGamalSecretKey) -> Self {
        ElGamalPubkey(&secret.0 * &(*H))
    }
```
After
```rust
#[allow(non_snake_case)]
    pub fn new(secret: &ElGamalSecretKey) -> Self {
        let s = &secret.0;
        assert!(s != &Scalar::zero());

        ElGamalPubkey(s.invert() * &(*H))
    }
```

# Fix Pattern

Centralize cryptographic key derivation in one helper, enforce the scalar precondition there, and route all keypair construction paths through that helper. Add focused proof tests for the affected key construction path.

## How It Was Fixed

`zk-token-sdk/src/encryption/elgamal.rs` was changed so `ElGamalPubkey::new` asserts the secret scalar is nonzero and derives the public key as `s.invert() * &(*H)`. `keygen_with_scalar` now creates the secret key and calls `ElGamalPubkey::new` instead of manually deriving the public key. `zk-token-sdk/src/sigma_proofs/pubkey_proof.rs` adds a derived-keypair case to the pubkey sigma proof correctness test.

# Why It Matters

1. ElGamal keypairs must have a consistent private/public relation.

2. Sigma proofs depend on the public key matching the corresponding secret key.

3. Duplicated cryptographic formulas can silently diverge across construction paths.

4. Rejecting zero secrets enforces a required precondition for inverse-scalar derivation.

# Evidence Notes

The production evidence is in `zk-token-sdk/src/encryption/elgamal.rs`: `ElGamalPubkey::new` changed from `&secret.0 * &(*H)` to `s.invert() * &(*H)` with a zero-scalar assertion, and `keygen_with_scalar` now delegates to it. The `pubkey_proof.rs` changes are test-only. The evidence supports an incorrect ElGamal key-derivation security fix. It does not support replay, signature-validation, malformed-proof-acceptance, or externally proven funds-loss claims. Protocol security invariant: ElGamal public keys in the zk-token SDK must be derived from a nonzero secret scalar using the same scheme-defined relation across all key construction paths, so proofs generated with a secret key verify against the corresponding public key. Verification notes: The patch does not show a replay or signature-validation bug. The patch does not by itself prove an externally exploitable funds-loss path. The evidence does not show malformed proof acceptance in the verifier beyond the corrected key relation. The zero-scalar handling is an assertion guard, not shown as a recoverable input-validation path. The changed pubkey_proof.rs code is test coverage, not production verifier logic. Do not classify this as replay or signature validation. Do not treat the pubkey proof test as production verifier logic. Exploitability is not established by the supplied evidence, so the verdict is likely rather than confirmed. The security relevance comes from corrected cryptographic key derivation in a zk-token SDK path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incorrect-cryptographic-key-derivation`
Final impact type: `cryptographic-integrity`
Final confidence: `medium`
Final tags: `cryptography, elgamal, key-derivation, zk-proofs`

The evidence supports retaining this as security hardening rather than a confirmed security fix. The production patch corrects canonical ElGamal public-key derivation and centralizes the nonzero scalar precondition in a cryptographic SDK path, which is security-sensitive. However, the supplied evidence does not prove an exploitable replay, signature-validation, malformed-proof-acceptance, or funds-loss issue, and the sigma proof changes shown are test coverage rather than verifier logic changes.

## Security Evidence

1. Production ElGamal public-key derivation changed from secret scalar multiplication to inverse-scalar multiplication by H.
2. The nonzero scalar assertion was moved into the canonical ElGamalPubkey::new derivation helper.
3. Scalar-based key generation now delegates to the canonical public-key derivation helper, removing divergent cryptographic formulas.
4. Added tests verify pubkey sigma proof correctness for a derived ElGamal keypair.

## Missing Evidence

1. No evidence of externally triggerable exploitability or asset loss.
2. No production verifier logic change showing malformed proofs were previously accepted.
3. No evidence supporting replay or signature-validation impact.
4. No evidence that the zero-scalar assertion handles untrusted recoverable input rather than an internal precondition.

## Claim Boundaries

1. Classify as incorrect cryptographic key derivation, not replay or signature validation.
2. Treat pubkey_proof.rs changes as test coverage, not production verifier hardening.
3. Do not claim confirmed exploitability or concrete funds loss from the supplied patch alone.
4. Security relevance is limited to tightening a cryptographic key relation in the zk-token SDK.
