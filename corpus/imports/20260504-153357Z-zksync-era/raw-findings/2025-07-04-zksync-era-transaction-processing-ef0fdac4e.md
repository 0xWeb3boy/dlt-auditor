---
case_id: case_20250704_ef0fdac4e
project: zksync-era
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-07-04
source_refs:
  - git:ef0fdac4e0ebe017e0ceb0cd7bbb6757a513ae38
  - "core/node/tee_proof_data_handler/src/tee_request_processor.rs:244"
  - "core/lib/crypto_primitives/src/ecdsa_signature.rs:194"
  - "core/node/tee_proof_data_handler/src/tee_request_processor.rs:4"
  - "core/node/tee_proof_data_handler/src/tee_request_processor.rs:21"
bug_class: signature-validation
impact_type:
  - proof-validation
confidence: medium
tags:
  - tee
  - signature-validation
  - crypto
  - input-validation
  - error-handling
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes TEE proof signature validation from raw `Signature::from_electrum` plus unchecked `recover(...).unwrap()` to `PackedEthSignature::deserialize_packed` plus checked signer recovery. This is security-relevant because it affects cryptographic validation on the TEE proof submission path, but the provided evidence does not prove proof forgery or show the full downstream signer authorization check.

## Observed Patch Facts

1. In `core/node/tee_proof_data_handler/src/tee_request_processor.rs`, the patch replaces `let signature = Signature::from_electrum(&proof.0.signature);` with `let signature = PackedEthSignature::deserialize_packed(&proof.0.signature)`.

2. In `core/lib/crypto_primitives/src/ecdsa_signature.rs`, the patch replaces `pub fn from_electrum(data: &[u8]) -> Self {` with `#[cfg(test)]`.

3. In `core/node/tee_proof_data_handler/src/tee_request_processor.rs`, the patch changes a sensitive implementation path.

4. In `core/node/tee_proof_data_handler/src/tee_request_processor.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `core/node/tee_proof_data_handler/src`, `core/node/tee_proof_data_handler`, `core/lib/crypto_primitives/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `core/node/tee_proof_data_handler/src/tests.rs`, `core/lib/crypto_primitives/src/packed_eth_signature.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/node/tee_proof_data_handler/src/tests.rs`, `core/node/tee_proof_data_handler/src/metrics.rs`. The strongest project-level identifiers around this patch are `signature`, `tee_types::TeeType`, `data`, and `proof`.

## Before/After Behavior

Before the patch, `submit_proof` verified that submitted proof bytes matched the L1 batch state root, parsed `proof.0.signature` with `Signature::from_electrum`, and then called `recover(&signature, &root_hash).unwrap()`. The referenced parser could return a fallback invalid signature for malformed input. After the patch, the processor parses with `PackedEthSignature::deserialize_packed`, maps parse failure to `Invalid signature`, and maps signer recovery failure to the same explicit request error. `Signature::from_electrum` is also restricted to test code.

# Root Cause

The TEE proof validation path used a lower-level Electrum-style signature parser and unchecked recovery on externally supplied proof data. The supported issue is weak signature format validation and error handling, not proven state corruption or accepted forged proof data.

## Walkthrough

1. A client submits a TEE proof for an `l1_batch_number` to `submit_proof`.

2. The processor retrieves the L1 batch state root and checks that `proof.0.proof` matches it.

3. Before the patch, the submitted signature was parsed with `Signature::from_electrum`, whose shown implementation can fall back to an invalid default signature for malformed input.

4. Before the patch, recovery used `recover(...).unwrap()`, so recovery failure was not converted into a normal invalid-signature response.

5. After the patch, signature bytes are parsed with `PackedEthSignature::deserialize_packed`.

6. After the patch, both signature deserialization failure and signer recovery failure return `GeneralError("Invalid signature")`.

7. The raw `Signature::from_electrum` helper is made test-only, reducing production use of that fallback parser.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/node/tee_proof_data_handler/src/tee_request_processor.rs | 244 | TEE proof submission validates the submitted proof root and recovers the signer from the packed Ethereum signature before saving or accepting proof data. |
| core/lib/crypto_primitives/src/ecdsa_signature.rs | 194 | Raw Electrum-style signature parser is removed from production visibility and kept only for tests. |
| core/node/tee_proof_data_handler/src/tee_request_processor.rs | 4 | TEE request processor switches its crypto primitive import from raw `Signature` to `PackedEthSignature`. |

## Code Snippets

## Snippet 1

Context: `core/node/tee_proof_data_handler/src/tee_request_processor.rs:244` (changes signature or replay validation logic)

Before
```rust
// Check for a valid signature
        let root_hash = H256::from_slice(proof.0.proof.as_slice());
        let signature = Signature::from_electrum(&proof.0.signature);
        let recovered_pubkey = recover(&signature, &root_hash).unwrap();

        /*
                let proof_address = public_to_address(&recovered_pubkey);
```
After
```rust
// Check for a valid signature
        let root_hash = H256::from_slice(proof.0.proof.as_slice());
        let signature = PackedEthSignature::deserialize_packed(&proof.0.signature)
            .map_err(|_| TeeProcessorError::GeneralError("Invalid signature".into()))?;
        let proof_address = signature
            .signature_recover_signer(&root_hash)
            .map_err(|_| TeeProcessorError::GeneralError("Invalid signature".into()))?;
```

## Snippet 2

Context: `core/lib/crypto_primitives/src/ecdsa_signature.rs:194` (changes a sensitive control or state-update path)

Before
```rust
/// Parse bytes as a signature encoded as RSV (V in "Electrum" notation).
    /// May return empty (invalid) signature if given data has invalid length.
    pub fn from_electrum(data: &[u8]) -> Self {
        if data.len() != 65 || data[64] < 27 {
            // fallback to empty (invalid) signature
```
After
```rust
/// Parse bytes as a signature encoded as RSV (V in "Electrum" notation).
    /// May return empty (invalid) signature if given data has invalid length.
    #[cfg(test)]
    pub(super) fn from_electrum(data: &[u8]) -> Self {
        if data.len() != 65 || data[64] < 27 {
            // fallback to empty (invalid) signature
```

## Snippet 3

Context: `core/node/tee_proof_data_handler/src/tee_request_processor.rs:4` (changes signature or replay validation logic)

Before
```rust
use chrono::{Duration as ChronoDuration, Utc};
use zksync_config::configs::TeeProofDataHandlerConfig;
use zksync_crypto_primitives::Signature;
use zksync_dal::{
    tee_proof_generation_dal::{LockedBatch, TeeProofGenerationJobStatus},
```
After
```rust
use chrono::{Duration as ChronoDuration, Utc};
use zksync_config::configs::TeeProofDataHandlerConfig;
use zksync_crypto_primitives::PackedEthSignature;
use zksync_dal::{
    tee_proof_generation_dal::{LockedBatch, TeeProofGenerationJobStatus},
```

## Snippet 4

Context: `core/node/tee_proof_data_handler/src/tee_request_processor.rs:21` (changes a sensitive control or state-update path)

Before
```rust
inputs::{TeeVerifierInput, V1TeeVerifierInput},
};
use zksync_types::{recover, tee_types::TeeType, L1BatchNumber, L2ChainId, H256};
use zksync_vm_executor::storage::L1BatchParamsProvider;
```
After
```rust
inputs::{TeeVerifierInput, V1TeeVerifierInput},
};
use zksync_types::aggregated_operations::AggregatedActionType::Tee;
use zksync_types::{tee_types::TeeType, L1BatchNumber, L2ChainId, H256};
use zksync_vm_executor::storage::L1BatchParamsProvider;
```

# Fix Pattern

Use the domain-specific packed Ethereum signature type at the external proof boundary, reject malformed signatures during parsing, and handle recovery failure as an explicit validation error.

## How It Was Fixed

`tee_request_processor.rs` imports `PackedEthSignature` instead of `Signature`, replaces `Signature::from_electrum(&proof.0.signature)` with `PackedEthSignature::deserialize_packed(&proof.0.signature)`, and replaces unchecked `recover(...).unwrap()` with `signature_recover_signer(&root_hash)` plus error mapping. `ecdsa_signature.rs` limits `Signature::from_electrum` to tests with `#[cfg(test)] pub(super)`.

# Why It Matters

1. TEE proof acceptance depends on cryptographic validation of submitted proof data.

2. Malformed signatures are now rejected explicitly instead of flowing through fallback parsing.

3. Unchecked recovery on request-controlled input is removed.

4. The evidence does not establish accepted forged proofs or state corruption.

# Evidence Notes

Grounded evidence comes from `core/node/tee_proof_data_handler/src/tee_request_processor.rs` around signature validation and `core/lib/crypto_primitives/src/ecdsa_signature.rs` around `Signature::from_electrum`. The stronger heuristic claims about transaction processing, state corruption, or inconsistent storage/accounting are unsupported. The downstream authorization comparison for the recovered signer is not shown, so impact should be limited to signature-format validation and checked failure handling in the TEE proof submission path. Protocol security invariant: A submitted TEE proof for an L1 batch should only proceed after the proof bytes match the batch state root and the submitted signature is decoded in the expected packed Ethereum format and successfully recovers a signer for that root hash. Malformed signature encoding or recovery failure should reject the request explicitly. Verification notes: The patch evidence does not prove that an attacker could forge an accepted TEE proof. The patch evidence does not show the full downstream comparison between recovered signer/address and an authorized TEE identity. The patch evidence does not prove state corruption despite the heuristic baseline suggesting it. The patch may also fix denial-of-service behavior from `unwrap()` on recovery failure, but impact is not fully established from the provided context. Confirmed direct replacement of `Signature::from_electrum` with `PackedEthSignature::deserialize_packed`. Confirmed removal of `recover(...).unwrap()` in the shown path. Confirmed `Signature::from_electrum` is made test-only in the provided diff. Not confirmed that malformed signatures could lead to accepted invalid proofs. Not confirmed how a panic would affect service availability at runtime. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-validation`
Final impact type: `proof-validation`
Final confidence: `medium`
Final tags: `tee, signature-validation, crypto, input-validation, error-handling`

The patch clearly tightens a security-sensitive TEE proof submission path by replacing a lower-level Electrum signature parser with the domain-specific packed Ethereum signature type, rejecting deserialization failures, and converting recovery failures into explicit validation errors instead of `unwrap()`. The evidence supports security hardening of cryptographic proof validation, but it does not prove accepted forged proofs, state corruption, or a concrete exploitable vulnerability, so the original security-fix/state-corruption framing is too strong.

## Security Evidence

1. TEE proof submission validates externally supplied signature bytes.
2. `Signature::from_electrum` is replaced with `PackedEthSignature::deserialize_packed`.
3. Malformed signature deserialization now returns `Invalid signature`.
4. Recovery failure now returns `Invalid signature` instead of panicking via `unwrap()`.
5. The raw `Signature::from_electrum` helper is restricted to test builds.

## Missing Evidence

1. No shown downstream authorization check tying the recovered signer to an allowed TEE identity.
2. No evidence that malformed signatures could previously be accepted as valid proofs.
3. No evidence of state corruption or transaction-processing integrity failure.
4. No runtime evidence showing whether the prior `unwrap()` caused exploitable denial of service.

## Claim Boundaries

1. Validate as security hardening, not a proven security fix.
2. Limit the bug class to signature/proof validation behavior.
3. Do not claim forged proof acceptance from the supplied patch alone.
4. Do not retain the original state-corruption impact claim.
