---
case_id: case_20230105_3e5e0566fd
project: sui
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2023-01-05
source_refs:
  - git:3e5e0566fd4c0e9a840fc961cf25344c66ed19c6
  - "crates/sui-types/src/crypto.rs:689"
  - "crates/sui-core/src/consensus_validator.rs:174"
  - "crates/sui-types/src/message_envelope.rs:292"
  - "crates/sui-types/src/crypto.rs:824"
bug_class: missing-user-signature-verification
impact_type:
  - invalid-certificate-acceptance
tags:
  - validator-ops
  - consensus
  - signature-validation
  - certificate-validation
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch is likely a security fix for Sui consensus certificate validation. The commit message explicitly says an unresolved TODO after unpinning user signatures allowed validators to submit certificates with incorrect user signatures. The supplied code evidence shows new regression support that corrupts `cert.tx_signature` and sends the resulting certificate messages through `SuiTxValidator::validate_batch`, plus helper mutability changes used to construct malformed test inputs. The provided excerpts do not show the actual validator guard or the final assertion, so the finding should be treated as likely rather than fully confirmed from code alone.

## Observed Patch Facts

1. In `crates/sui-types/src/crypto.rs`, the patch replaces `impl signature::Signature for Signature {` with `impl AsMut<[u8]> for Signature {`.

2. In `crates/sui-core/src/consensus_validator.rs`, the patch adds `let bogus_transaction_bytes: Vec<_> = certificates`.

3. In `crates/sui-types/src/message_envelope.rs`, the patch replaces `impl<T: Message, S> From<VerifiedEnvelope<T, S>> for Envelope<T, S> {` with `impl<T: Message, S> DerefMut for Envelope<T, S> {`.

4. In `crates/sui-types/src/crypto.rs`, the patch replaces `impl signature::Signature for Secp256k1SuiSignature {` with `impl AsMut<[u8]> for Secp256k1SuiSignature {`.

## Project Context

The changed code sits primarily in `crates/sui-types/src`, `crates/sui-types`, `crates/sui-core/src`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/sui-types/src/certificate_proof.rs`, `crates/sui-types/src/signature_seed.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/checkpoints/mod.rs`, `crates/sui-types/src/messages_checkpoint.rs`. The strongest project-level identifiers around this patch are `as_mut`, `Signature`, `impl`, and `cert`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/authority_tests.rs`, `crates/sui-types/src/unit_tests/signature_seed_tests.rs`.

## Before/After Behavior

Before the change, the described issue was that consensus certificate validation could accept certificates even when the embedded user transaction signature was incorrect. After the change, the intended behavior is that certificate messages submitted through consensus batch validation are checked against the embedded user signature and rejected when that signature has been altered. The visible code evidence supports this through a negative test setup that mutates `cert.tx_signature` before serialization, but the excerpt does not include the implementation of the check or the final assertion.

# Root Cause

Incomplete validation at the consensus certificate boundary: after user signatures were unpinned from certificates, the consensus validator apparently did not re-verify that the embedded user transaction signature remained valid for the transaction being certified.

## Walkthrough

1. The commit message identifies a vulnerability in `consensus_validator` related to unpinned user signatures in certificates.

2. The reported bad case is validators submitting certificates with incorrect user signatures.

3. The test setup first exercises valid certificate messages through `SuiTxValidator::validate` and `validate_batch`.

4. The new negative test path mutates a byte in `cert.tx_signature` using `as_mut()[2].wrapping_add(1)`.

5. The corrupted certificates are serialized as `ConsensusTransaction::new_certificate_message` values and placed into a `Batch`.

6. The batch is passed to `validator.validate_batch`, tying the malformed user signature to the consensus validation path.

7. Helper changes add mutable access to signature and envelope internals; these appear to support malformed test construction, not to be the root security fix themselves.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/consensus_validator.rs | 174 | consensus batch validation path rejects certificate messages whose embedded user transaction signature has been corrupted |
| crates/sui-types/src/crypto.rs | 689 | signature byte mutability support used to construct malformed signature test inputs |
| crates/sui-types/src/message_envelope.rs | 292 | envelope data mutability support used around certificate/message manipulation |
| crates/sui-types/src/crypto.rs | 824 | scheme-specific signature byte mutability support for malformed signature construction |

## Code Snippets

## Snippet 1

Context: `crates/sui-types/src/crypto.rs:689` (changes signature or replay validation logic)

Before
```rust
}
}

impl signature::Signature for Signature {
```
After
```rust
}
}
impl AsMut<[u8]> for Signature {
    fn as_mut(&mut self) -> &mut [u8] {
        match self {
            Signature::Ed25519SuiSignature(sig) => sig.as_mut(),
            Signature::Secp256k1SuiSignature(sig) => sig.as_mut(),
            Signature::Secp256r1SuiSignature(sig) => sig.as_mut(),
```

## Snippet 2

Context: `crates/sui-core/src/consensus_validator.rs:174` (changes a consensus- or validator-sensitive branch)

Before
```rust
let res_batch = validator.validate_batch(&batch);
        assert!(res_batch.is_ok(), "{res_batch:?}");
    }
}
```
After
```rust
let res_batch = validator.validate_batch(&batch);
        assert!(res_batch.is_ok(), "{res_batch:?}");

        let bogus_transaction_bytes: Vec<_> = certificates
            .into_iter()
            .map(|mut cert| {
                cert.tx_signature.as_mut()[2] = cert.tx_signature.as_mut()[2].wrapping_add(1);
                bincode::serialize(&ConsensusTransaction::new_certificate_message(&name1, cert))
```

## Snippet 3

Context: `crates/sui-types/src/message_envelope.rs:292` (changes a sensitive control or state-update path)

Before
```rust
}

impl<T: Message, S> From<VerifiedEnvelope<T, S>> for Envelope<T, S> {
    fn from(v: VerifiedEnvelope<T, S>) -> Self {
```
After
```rust
}

impl<T: Message, S> DerefMut for Envelope<T, S> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.data
    }
}
```

## Snippet 4

Context: `crates/sui-types/src/crypto.rs:824` (changes a sensitive control or state-update path)

Before
```rust
}

impl signature::Signature for Secp256k1SuiSignature {
    fn from_bytes(bytes: &[u8]) -> Result<Self, signature::Error> {
```
After
```rust
}

impl AsMut<[u8]> for Secp256k1SuiSignature {
    fn as_mut(&mut self) -> &mut [u8] {
        self.0.as_mut()
    }
}
```

# Fix Pattern

Verify embedded user transaction signatures during consensus certificate-message validation, and add regression coverage that submits otherwise well-formed certificates with deliberately corrupted user signatures.

## How It Was Fixed

Based on the commit subject and message, the consensus validator was changed to verify certificate user signatures. The visible excerpts show supporting regression-test construction: mutable signature access was added for `Signature` and `Secp256k1SuiSignature`, `DerefMut` was added for `Envelope<T, S>`, and `consensus_validator.rs` creates corrupted certificate messages for `validate_batch`. The actual validation guard is not shown in the supplied snippets.

# Why It Matters

1. Consensus should not accept a certificate solely because validator-side certificate structure is present.

2. An incorrect embedded user signature breaks the link between the transaction and user authorization.

3. The evidence supports a missing user-signature validation issue, not replay, direct theft, or arbitrary transaction forgery.

4. Batch validation is security-sensitive because malformed certificate messages can enter through consensus batches.

# Evidence Notes

Strongest evidence is the commit subject `[consensus] Verify certificate user signature (#7175)` and body stating that the issue allowed validators to submit certificates with incorrect user signatures. Code excerpts show test/support changes in `crates/sui-core/src/consensus_validator.rs`, `crates/sui-types/src/crypto.rs`, and `crates/sui-types/src/message_envelope.rs`. The supplied snippets do not show the actual validation implementation or the final rejection assertion, so claims about concrete rejection behavior should remain qualified. Protocol security invariant: Consensus certificate validation must verify that the embedded user transaction signature is still valid for the transaction data; validator or certificate structure alone must not make a certificate acceptable if the user signature is incorrect. Verification notes: The evidence does not prove arbitrary transaction forgery beyond acceptance of certificates with incorrect user signatures. The evidence does not show direct fund theft, object mutation, or final execution effects from the malformed certificate. The helper trait changes alone are not security fixes; the security relevance comes from the consensus validator certificate-signature check. The evidence does not establish a replay vulnerability, only a missing or incomplete user signature validation invariant. Do not classify this as replay; the provided evidence supports missing user-signature verification only. Do not claim direct fund theft, object mutation, or arbitrary transaction forgery from the supplied evidence. Treat `AsMut` and `DerefMut` additions as support code unless fuller diff evidence shows otherwise. Confidence is medium because the commit message is explicit, but the core guard is not visible in the supplied excerpts. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `missing-user-signature-verification`
Final impact type: `invalid-certificate-acceptance`
Final tags: `validator-ops, consensus, signature-validation, certificate-validation, validator`

The commit metadata explicitly states a vulnerability in consensus validation that allowed validators to submit certificates with incorrect user signatures, and the supplied patch evidence adds a consensus-validator regression path that corrupts cert.tx_signature before submitting certificate messages through validate_batch. The excerpts do not show the actual validation guard or final rejection assertion, so this should remain likely rather than confirmed, but the evidence is strong enough to retain as a security-fix case. The original replay/request-forgery framing is broader than the evidence supports.

## Security Evidence

1. Commit subject says certificate user signatures are verified in consensus.
2. Commit body states incorrect user signatures exposed a vulnerability.
3. Test evidence mutates cert.tx_signature bytes before serializing certificate messages.
4. Malformed certificates are submitted through ConsensusTransaction::new_certificate_message and validate_batch.
5. Helper mutability changes appear to support constructing corrupted signature test inputs.

## Missing Evidence

1. Actual consensus_validator implementation guard is not shown.
2. Final assertion proving corrupted certificates are rejected is not shown in the excerpts.
3. No evidence shows replay behavior, direct transaction forgery, fund theft, or execution impact.

## Claim Boundaries

1. Supported claim: consensus certificate validation failed to reject certificates with incorrect embedded user signatures.
2. Do not claim replay based on the supplied evidence.
3. Do not claim arbitrary transaction forgery or direct asset loss.
4. Treat AsMut and DerefMut additions as test/support mechanics, not the security fix by themselves.
