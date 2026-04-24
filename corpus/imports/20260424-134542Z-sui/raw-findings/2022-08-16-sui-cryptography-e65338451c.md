---
case_id: case_20220816_e65338451c
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2022-08-16
source_refs:
  - git:e65338451cb82c05987bbe4b581129008b66d360
  - "narwhal/crypto/src/traits.rs:99"
  - "narwhal/crypto/src/ed25519.rs:78"
  - "narwhal/crypto/src/bls12381.rs:192"
  - "narwhal/crypto/src/bls12377/mod.rs:267"
bug_class: empty-batch-signature-validation
impact_type:
  - signature-verification-bypass
tags:
  - cryptography
  - signature-validation
  - batch-verification
  - empty-batch
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens Narwhal's batch signature verification paths by adding explicit rejection of empty signature batches in the generic `VerifyingKey` default and in Ed25519, BLS12-381, and BLS12-377 implementations. The evidence supports a crypto validation hardening finding, but does not establish a concrete remote exploit, transaction forgery, replay issue, or consensus impact.

## Observed Patch Facts

1. In `narwhal/crypto/src/traits.rs`, the patch replaces `fn verify_batch(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), signature...` with `fn verify_batch_empty_fail(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<()...`.

2. In `narwhal/crypto/src/ed25519.rs`, the patch replaces `fn verify_batch(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), signature...` with `fn verify_batch_empty_fail(`.

3. In `narwhal/crypto/src/bls12381.rs`, the patch replaces `fn verify_batch(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), signature...` with `fn verify_batch_empty_fail(`.

4. In `narwhal/crypto/src/bls12377/mod.rs`, the patch replaces `fn verify_batch(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), signature...` with `fn verify_batch_empty_fail(`.

## Project Context

The changed code sits primarily in `narwhal/crypto/src`, `narwhal/crypto`, `narwhal/crypto/src/bls12377`, which anchors the finding in the `cryptography` area of the project. Historical context from `narwhal/crypto/src/secp256k1.rs`, `narwhal/crypto/src/pubkey_bytes.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `narwhal/crypto/src/secp256k1.rs`, `narwhal/crypto/src/pubkey_bytes.rs`. The strongest project-level identifiers around this patch are `Self::Sig`, `sigs`, `signature::Error`, and `eyre::Report`. Nearby tests or test-like files include `narwhal/crypto/src/tests/secp256k1_tests.rs`, `narwhal/crypto/src/tests/ed25519_tests.rs`.

## Before/After Behavior

Before the patch, the shown `verify_batch` implementations checked key/signature count mismatches but did not show an explicit `sigs.is_empty()` rejection; an empty public-key list and empty signature list would pass the length-equality check in the generic path. After the patch, the shown implementations use `verify_batch_empty_fail(...) -> Result<(), eyre::Report>` and return an error when `sigs.is_empty()` before continuing with batch verification.

# Root Cause

The batch verification boundary handled mismatched key/signature counts but lacked an explicit guard for the degenerate empty-batch case, allowing an empty input set to reach or pass normal verification behavior in at least the generic path.

## Walkthrough

1. The generic `VerifyingKey` batch verification path previously checked whether public-key and signature counts differed.

2. For two empty slices, that mismatch check would not fail, and the shown generic iterator-based behavior would have no signature/public-key pair to verify.

3. The patch adds an explicit `sigs.is_empty()` check to the generic batch verification helper and returns an error for empty batches.

4. The Ed25519 implementation now performs the same empty-signature-batch rejection before invoking its batch verifier logic.

5. The BLS12-381 implementation now rejects empty signature batches before proceeding with its batch verification setup.

6. The BLS12-377 implementation now rejects empty signature batches before its batch verification flow.

7. The shown patched paths also preserve rejection of mismatched public-key and signature counts, now with descriptive `eyre::Report` errors.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| narwhal/crypto/src/traits.rs | 99 | default VerifyingKey batch verification now rejects empty signature batches and key/signature count mismatches |
| narwhal/crypto/src/ed25519.rs | 78 | Ed25519 batch verification implementation now rejects empty signature batches before verifying |
| narwhal/crypto/src/bls12381.rs | 192 | BLS12-381 batch verification implementation now rejects empty signature batches before randomized batch checking |
| narwhal/crypto/src/bls12377/mod.rs | 267 | BLS12-377 batch verification implementation now rejects empty signature batches before batch verification |

## Code Snippets

## Snippet 1

Context: `narwhal/crypto/src/traits.rs:99` (changes signature or replay validation logic)

Before
```rust
// Expected to be overridden by implementations
    fn verify_batch(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), signature::Error> {
        if pks.len() != sigs.len() {
            return Err(signature::Error::new());
        }
        pks.iter()
            .zip(sigs)
```
After
```rust
// Expected to be overridden by implementations
    fn verify_batch_empty_fail(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), eyre::Report> {
        if sigs.is_empty() {
            return Err(eyre!("Critical Error! This behavious can signal something dangerous, and that someone may be trying to bypass signature verification through providing empty batches."));
        }
        if pks.len() != sigs.len() {
            return Err(eyre!("Mismatch between number of signatures and public keys provided"));
```

## Snippet 2

Context: `narwhal/crypto/src/ed25519.rs:78` (changes signature or replay validation logic)

Before
```rust
const LENGTH: usize = ED25519_PUBLIC_KEY_LENGTH;

    fn verify_batch(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), signature::Error> {
        let mut batch = batch::Verifier::new();
```
After
```rust
const LENGTH: usize = ED25519_PUBLIC_KEY_LENGTH;

    fn verify_batch_empty_fail(
        msg: &[u8],
        pks: &[Self],
        sigs: &[Self::Sig],
    ) -> Result<(), eyre::Report> {
        if sigs.is_empty() {
```

## Snippet 3

Context: `narwhal/crypto/src/bls12381.rs:192` (changes signature or replay validation logic)

Before
```rust
const LENGTH: usize = BLS_PUBLIC_KEY_LENGTH;

    fn verify_batch(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), signature::Error> {
        let num_sigs = sigs.len();
        if pks.len() != num_sigs {
            return Err(signature::Error::new());
        }
        let mut rands: Vec<blst_scalar> = Vec::with_capacity(num_sigs);
```
After
```rust
const LENGTH: usize = BLS_PUBLIC_KEY_LENGTH;

    fn verify_batch_empty_fail(
        msg: &[u8],
        pks: &[Self],
        sigs: &[Self::Sig],
    ) -> Result<(), eyre::Report> {
        let num_sigs = sigs.len();
```

## Snippet 4

Context: `narwhal/crypto/src/bls12377/mod.rs:267` (changes signature or replay validation logic)

Before
```rust
const LENGTH: usize = CELO_BLS_PUBLIC_KEY_LENGTH;

    fn verify_batch(msg: &[u8], pks: &[Self], sigs: &[Self::Sig]) -> Result<(), signature::Error> {
        if pks.len() != sigs.len() {
            return Err(signature::Error::new());
        }
        let mut batch = celo_bls::bls::Batch::new(msg, &[]);
```
After
```rust
const LENGTH: usize = CELO_BLS_PUBLIC_KEY_LENGTH;

    fn verify_batch_empty_fail(
        msg: &[u8],
        pks: &[Self],
        sigs: &[Self::Sig],
    ) -> Result<(), eyre::Report> {
        if sigs.is_empty() {
```

# Fix Pattern

Add an explicit non-empty-batch precondition at batch signature verification entry points, before curve-specific verification logic, while preserving key/signature count mismatch checks.

## How It Was Fixed

The trait default and the Ed25519, BLS12-381, and BLS12-377 implementations were changed to `verify_batch_empty_fail(...) -> Result<(), eyre::Report>` and now return an error when `sigs.is_empty()`. The error text explicitly describes empty batches as potentially dangerous and possibly indicative of a signature-verification bypass attempt.

# Why It Matters

1. Successful batch verification can be used by callers as evidence that signatures were checked.

2. An empty signature list is a degenerate input that can pass simple length-equality validation.

3. Rejecting empty batches makes the verification contract less ambiguous.

4. The provided evidence does not prove a higher-level exploit path or consensus failure.

# Evidence Notes

Grounded evidence comes from changed excerpts in `narwhal/crypto/src/traits.rs`, `narwhal/crypto/src/ed25519.rs`, `narwhal/crypto/src/bls12381.rs`, and `narwhal/crypto/src/bls12377/mod.rs`, all adding `sigs.is_empty()` rejection with an error message warning about bypassing signature verification. The evidence does not show higher-level caller behavior in `narwhal/types/src/primary.rs`, remote reachability, replay mechanics, private key compromise, transaction forgery, or consensus impact. Claims about replay-sensitive validation should be removed because no replay-specific mechanism is shown. Protocol security invariant: Batch signature verification should not report success for an empty signature set; success should imply that at least one signature/public-key pair was actually checked, and key/signature count mismatches must fail. Verification notes: No remote exploit path is proven by the patch evidence. No consensus safety or transaction-forgery impact is shown directly. No replay vulnerability is demonstrated beyond the signature-batch validation issue. No evidence shows private key compromise or signature forgery. The higher-level caller behavior in narwhal/types/src/primary.rs is not shown in the provided excerpts. Confirmed from provided excerpts: empty signature batches are now rejected in multiple crypto implementations. Confirmed from provided excerpts: key/signature count mismatch rejection remains present. Not established by provided evidence: exploitability through a network-facing caller. Not established by provided evidence: replay, transaction forgery, or consensus safety impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `empty-batch-signature-validation`
Final impact type: `signature-verification-bypass`
Final tags: `cryptography, signature-validation, batch-verification, empty-batch, security-hardening`

The supplied patch evidence supports retaining this as security hardening: multiple batch signature verification implementations now explicitly reject empty signature batches, and the new error message directly frames empty batches as a possible signature-verification bypass attempt. The evidence does not prove a concrete exploit path, replay attack, transaction forgery, or consensus impact, so the original replay/request-forgery framing should be narrowed.

## Security Evidence

1. Batch verification paths in the generic trait, Ed25519, BLS12-381, and BLS12-377 now reject `sigs.is_empty()`.
2. The previous shown logic rejected count mismatches but did not explicitly reject zero signatures where public keys and signatures could both be empty.
3. The added error text explicitly identifies empty batches as dangerous and potentially related to bypassing signature verification.
4. The changes are in cryptographic verification code and are accompanied by related test updates according to the commit metadata.

## Missing Evidence

1. No higher-level caller or network-facing path is shown accepting attacker-controlled empty batches.
2. No proof is shown that empty-batch success caused transaction forgery, replay, or consensus failure.
3. No concrete vulnerability advisory, exploit scenario, or security issue reference is supplied.
4. The evidence does not establish private-key compromise or cryptographic signature forgery.

## Claim Boundaries

1. Keep the finding as security hardening, not a proven exploitable security fix.
2. Describe the issue as empty-batch signature verification hardening.
3. Do not claim replay, request forgery, transaction forgery, or consensus impact from the provided evidence alone.
4. Do not claim remote exploitability unless supported by additional caller evidence.
