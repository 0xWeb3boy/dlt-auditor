---
case_id: case_20251021_1979ab3fc2
project: stacks-core
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2025-10-21
source_refs:
  - git:1979ab3fc2c1af329881cda6333dd284f90a0785
  - "stacks-common/src/util/secp256r1.rs:173"
  - "stacks-common/src/util/secp256r1.rs:400"
  - "stacks-common/src/util/secp256r1.rs:318"
  - "stacks-common/src/util/secp256r1.rs:386"
bug_class: ambiguous-crypto-verification-api
impact_type:
  - signature-verification-misuse-risk
confidence: medium
tags:
  - blockchain-core
  - cryptography
  - signature-verification
  - api-hardening
  - typed-errors
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The commit changes the secp256r1 verification API from returning Result<bool, &'static str> to returning Result<(), Secp256r1Error>. Invalid signatures now return Err(Secp256r1Error::InvalidSignature) instead of Ok(false), and tests were updated to match that contract. This is security-relevant crypto API hardening, but the evidence does not establish a concrete vulnerability or accepted invalid-signature path.

## Observed Patch Facts

1. In `stacks-common/src/util/secp256r1.rs`, the patch replaces `) -> Result<bool, &'static str> {` with `/// Returns Ok(()) if the signature is valid, or an error otherwise.`.

2. In `stacks-common/src/util/secp256r1.rs`, the patch replaces `let valid = pubk2.verify_digest(&msg_hash, &sig).unwrap();` with `let e = pubk2`.

3. In `stacks-common/src/util/secp256r1.rs`, the patch replaces `if message_arr.len() != 32 {` with `let msg: &[u8; 32] = message_arr`.

4. In `stacks-common/src/util/secp256r1.rs`, the patch replaces `let valid = pubk.verify_digest(&msg_hash, &sig).unwrap();` with `pubk.verify_digest(&msg_hash, &sig)`.

## Project Context

The changed code sits primarily in `stacks-common/src/util`, `stacks-common/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `stacks-common/src/util/secp256k1.rs`, `stacks-common/src/util/vrf.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stacks-common/src/util/secp256k1.rs`. The strongest project-level identifiers around this patch are `Secp256r1Error::InvalidSignature`, `msg_hash`, `Secp256r1Error::InvalidMessage`, and `Secp256r1Error`. Nearby tests or test-like files include `stacks-common/src/deps_common/httparse_tests/mod.rs`.

## Before/After Behavior

Before the patch, verify_digest returned Result<bool, &'static str>: valid signatures produced Ok(true), invalid signatures produced Ok(false), and malformed inputs produced error strings. After the patch, verify_digest returns Result<(), Secp256r1Error>: valid signatures produce Ok(()), malformed messages produce InvalidMessage, and malformed or non-matching signatures produce InvalidSignature. The secp256r1_verify helper also changed explicit length checks to try_into conversions mapped to the same typed errors, which appears behaviorally equivalent from the supplied evidence.

# Root Cause

The grounded issue is an ambiguous API contract: invalid signatures were represented as a successful Result containing false, while other invalid inputs were represented as errors. This could be easier for callers to misuse, but no provided evidence shows an actual misuse or downstream security bypass.

## Walkthrough

1. The changed code is in stacks-common/src/util/secp256r1.rs.

2. Before the patch, Secp256r1PublicKey::verify_digest returned Result<bool, &'static str>.

3. The old implementation returned Ok(true) for valid signatures and Ok(false) for cryptographic verification failure.

4. After the patch, verify_digest returns Result<(), Secp256r1Error>.

5. The patched implementation returns Ok(()) only for successful verification.

6. Invalid message length maps to Secp256r1Error::InvalidMessage.

7. Signature decoding failure and verification failure map to Secp256r1Error::InvalidSignature.

8. The valid-signature test now expects success without a boolean result.

9. The mismatched-key test now expects InvalidSignature instead of Ok(false).

10. The secp256r1_verify helper now uses try_into for fixed-size array conversion while preserving the same error categories.

11. No supplied evidence shows invalid signatures being accepted by a production caller, reaching state-changing logic, bypassing signer binding, or enabling replay.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stacks-common/src/util/secp256r1.rs | 173 | Secp256r1PublicKey::verify_digest now returns Result<(), Secp256r1Error> and treats invalid signatures as errors |
| stacks-common/src/util/secp256r1.rs | 315 | secp256r1_verify converts message and signature byte slices into fixed-size arrays with typed validation errors |
| stacks-common/src/util/secp256r1.rs | 380 | valid signature test updated to expect Ok(()) |
| stacks-common/src/util/secp256r1.rs | 393 | mismatched-key test updated to expect Secp256r1Error::InvalidSignature |

## Code Snippets

## Snippet 1

Context: `stacks-common/src/util/secp256r1.rs:173` (changes signature or replay validation logic)

Before
```rust
/// Verify a signature against a message hash.
    pub fn verify_digest(
        &self,
        msg_hash: &[u8],
        sig: &MessageSignature,
    ) -> Result<bool, &'static str> {
        if msg_hash.len() != 32 {
```
After
```rust
/// Verify a signature against a message hash.
    /// Returns Ok(()) if the signature is valid, or an error otherwise.
    pub fn verify_digest(
        &self,
        msg_hash: &[u8],
        sig: &MessageSignature,
    ) -> Result<(), Secp256r1Error> {
```

## Snippet 2

Context: `stacks-common/src/util/secp256r1.rs:400` (changes the branch that decides whether execution stops or continues)

Before
```rust
let sig = privk1.sign(&msg_hash).unwrap();
        let valid = pubk2.verify_digest(&msg_hash, &sig).unwrap();

        assert!(!valid);
    }
```
After
```rust
let sig = privk1.sign(&msg_hash).unwrap();
        let e = pubk2
            .verify_digest(&msg_hash, &sig)
            .expect_err("expected an error");
        assert_eq!(e, Secp256r1Error::InvalidSignature);
    }
```

## Snippet 3

Context: `stacks-common/src/util/secp256r1.rs:318` (changes a sensitive control or state-update path)

Before
```rust
pubkey_arr: &[u8],
) -> Result<(), Secp256r1Error> {
    if message_arr.len() != 32 {
        return Err(Secp256r1Error::InvalidMessage);
    }

    if signature_arr.len() != 64 {
        return Err(Secp256r1Error::InvalidSignature);
```
After
```rust
pubkey_arr: &[u8],
) -> Result<(), Secp256r1Error> {
    let msg: &[u8; 32] = message_arr
        .try_into()
        .map_err(|_| Secp256r1Error::InvalidMessage)?;
    let sig_bytes: &[u8; 64] = signature_arr
        .try_into()
        .map_err(|_| Secp256r1Error::InvalidSignature)?;
```

## Snippet 4

Context: `stacks-common/src/util/secp256r1.rs:386` (changes signature or replay validation logic)

Before
```rust
let sig = privk.sign(&msg_hash).unwrap();
        let valid = pubk.verify_digest(&msg_hash, &sig).unwrap();

        assert!(valid);
    }
```
After
```rust
let sig = privk.sign(&msg_hash).unwrap();
        pubk.verify_digest(&msg_hash, &sig)
            .expect("invalid signature");
    }
```

# Fix Pattern

Clarify cryptographic verification APIs so success is represented only by Ok(()) and verification failure is represented by a typed error, avoiding a Result success case for invalid signatures.

## How It Was Fixed

The patch changed verify_digest to return Result<(), Secp256r1Error>, replaced string errors with typed Secp256r1Error variants, mapped mismatched signatures to InvalidSignature, and updated tests to assert the new success and failure contract. The public secp256r1_verify helper was mechanically adjusted to use fixed-size array conversions with equivalent typed error mapping.

# Why It Matters

1. Cryptographic verification APIs should make successful verification unambiguous.

2. Ok(false) for an invalid signature can be easier to misuse than an error return.

3. Typed errors make failure handling more consistent.

4. The evidence supports hardening, not a confirmed vulnerability.

# Evidence Notes

Evidence is limited to the secp256r1 utility and tests in stacks-common/src/util/secp256r1.rs. The commit message says the signature was changed to avoid potentially confusing usage. The diff supports an API cleanup and hardening interpretation, but does not show a vulnerable caller or exploit path. Claims about replay, state-transition bypass, signer-binding failure, or accepted invalid signatures are unsupported. Protocol security invariant: Secp256r1 verification should have an unambiguous success contract: a correctly sized message digest, well-formed signature, and matching public key are required for successful verification. The patch changes invalid-signature results from Ok(false) to a typed error, but the supplied evidence does not show a production caller that confused Ok(false) with acceptance. Verification notes: No provided evidence shows a production caller that ignored the boolean result and accepted an invalid signature. No replay, nonce, signer-binding, or state-transition bypass is demonstrated by the patch. The try_into rewrite appears equivalent to prior length checks and does not by itself prove stricter validation. Exploitability is not established from the commit message or diff evidence alone. Confirmed by supplied diff: verify_digest changed from Result<bool, &'static str> to Result<(), Secp256r1Error>. Confirmed by supplied tests: mismatched-key verification now expects InvalidSignature instead of Ok(false). The try_into rewrite in secp256r1_verify appears equivalent to prior length checks based on the provided snippets. No production misuse of the old boolean return is shown. No concrete vulnerability thesis is established by the provided evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `ambiguous-crypto-verification-api`
Final impact type: `signature-verification-misuse-risk`
Final confidence: `medium`
Final tags: `blockchain-core, cryptography, signature-verification, api-hardening, typed-errors`

The supplied patch does not prove a concrete exploitable vulnerability or replay/signature bypass, but it does harden a security-sensitive cryptographic verification API. Invalid signatures previously returned a successful Result value, Ok(false), which could be misused by callers that only checked for Err or used propagation patterns. The new contract makes successful verification unambiguous as Ok(()) and maps invalid signatures to a typed error. This supports security-hardening, not a confirmed security-fix.

## Security Evidence

1. secp256r1 verification API changed from Result<bool, &'static str> to Result<(), Secp256r1Error>.
2. Invalid signatures changed from Ok(false) to Err(Secp256r1Error::InvalidSignature).
3. Tests were updated so mismatched-key verification must produce InvalidSignature rather than a false success value.
4. The commit message says the signature was changed to avoid potentially confusing usage in a cryptographic verification method.

## Missing Evidence

1. No production caller is shown misinterpreting Ok(false) as accepted verification.
2. No state transition, authentication, replay, or signer-binding bypass is demonstrated.
3. No exploit scenario or external input path is provided.
4. The try_into rewrite appears behaviorally equivalent to prior explicit length checks.

## Claim Boundaries

1. Classify as API hardening for cryptographic signature verification, not a confirmed vulnerability fix.
2. Do not claim accepted invalid signatures occurred in production.
3. Do not claim replay prevention or request forgery impact from the supplied evidence.
4. Do not treat the length-check rewrite as independently security-relevant without more evidence.
