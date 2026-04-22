---
case_id: case_20260307_3e0b436b4
project: base
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2026-03-07
source_refs:
  - git:3e0b436b48d6dcbd167f0ce2e69458b0a7126ccc
  - "crates/proof/proposer/src/output_proposer.rs:59"
  - "crates/proof/proposer/src/output_proposer.rs:508"
  - "crates/proof/tee/client/src/client_error.rs:18"
  - "crates/proof/tee/core/src/error.rs:23"
bug_class: signature-validation
impact_type:
  - malformed-input-acceptance
confidence: medium
tags:
  - blockchain-core
  - tee
  - proof-encoding
  - signature-validation
  - cryptographic-input-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence shows a refactor plus validation tightening in the TEE proof-encoding path: proposer-local proof assembly was replaced with a shared `ProofEncoder`, and invalid ECDSA `v` values are now surfaced explicitly. That supports a claim of stronger signature-format validation, but it does not establish that a real vulnerability existed or that malformed proofs were previously accepted end-to-end.

## Observed Patch Facts

1. In `crates/proof/proposer/src/output_proposer.rs`, the patch replaces `let sig = &proposal.output.signature;` with `ProofEncoder::encode_proof_bytes(`.

2. In `crates/proof/proposer/src/output_proposer.rs`, the patch replaces `assert!(result.unwrap_err().to_string().contains("unexpected ECDSA v-value"));` with `assert!(result.unwrap_err().to_string().contains("invalid ECDSA v-value"));`.

3. In `crates/proof/tee/client/src/client_error.rs`, the patch adds `impl ClientError {`.

4. In `crates/proof/tee/core/src/error.rs`, the patch adds `/// Invalid ECDSA v-value.`.

## Project Context

The changed code sits primarily in `crates/proof/proposer/src`, `crates/proof/proposer`, `crates/proof/tee/client/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/proof/tee/core/src/proof.rs`, `crates/proof/tee/core/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/proof/proposer/src/prover/mod.rs`, `crates/proof/proposer/src/driver/mod.rs`. The strongest project-level identifiers around this patch are `ProposerError::Internal`, `proposal`, `result`, and `value`.

## Before/After Behavior

Before the change, the visible proposer code manually assembled proof bytes after checking signature length. After the change, it delegates encoding to `ProofEncoder::encode_proof_bytes(...)`, and the shared error surface now includes explicit rejection of invalid ECDSA `v` values; a regression test covers that case.

# Root Cause

The visible issue is inconsistent ownership of proof encoding and validation in a sensitive path: proposer-local code performed ad hoc assembly with length checking, while stricter structural validation was not shown there. The patch centralizes that logic in a shared encoder.

## Walkthrough

1. `build_proof_data()` in `crates/proof/proposer/src/output_proposer.rs` previously performed local proof-byte construction after a signature-length check.

2. The patched version replaces that local construction with `ProofEncoder::encode_proof_bytes(...)`, moving encoding and validation into shared TEE-core code.

3. `crates/proof/tee/core/src/error.rs` adds `CryptoError::InvalidVValue(u8)`, which is concrete evidence that unsupported ECDSA recovery-byte values are now explicitly rejected.

4. The regression test in `crates/proof/proposer/src/output_proposer.rs` mutates the signature `v` byte to `5` and asserts that proof building fails with `invalid ECDSA v-value`.

5. The supplied evidence does not show prior acceptance by the enclave or on-chain verifier, so the security impact remains unproven.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/proof/proposer/src/output_proposer.rs | 46 | Builds the proof payload for verifier initialization; now delegates to the shared encoder instead of locally assembling proof bytes. |
| crates/proof/tee/core/src/proof.rs | 1 | Defines the shared TEE proof wire-format constants and `ProofEncoder` used to enforce signature-format invariants. |
| crates/proof/tee/core/src/error.rs | 17 | Introduces an explicit cryptographic error for invalid ECDSA `v` values, indicating newly enforced validation. |
| crates/proof/proposer/src/output_proposer.rs | 502 | Regression test covering rejection of malformed signature recovery-byte values in the proposal submission path. |

## Code Snippets

## Snippet 1

Context: `crates/proof/proposer/src/output_proposer.rs:59` (changes signature or replay validation logic)

Before
```rust
/// Matches Go's `buildProofData()` in `driver.go`.
pub fn build_proof_data(proposal: &ProverProposal) -> Result<Bytes, ProposerError> {
    let sig = &proposal.output.signature;
    if sig.len() < ECDSA_SIGNATURE_LENGTH {
        return Err(ProposerError::Internal(format!(
            "signature too short: expected at least {ECDSA_SIGNATURE_LENGTH} bytes, got {}",
            sig.len()
        )));
```
After
```rust
/// Matches Go's `buildProofData()` in `driver.go`.
pub fn build_proof_data(proposal: &ProverProposal) -> Result<Bytes, ProposerError> {
    ProofEncoder::encode_proof_bytes(
        &proposal.output.signature,
        proposal.to.l1origin.hash,
        proposal.to.l1origin.number,
    )
    .map_err(|e| ProposerError::Internal(e.to_string()))
```

## Snippet 2

Context: `crates/proof/proposer/src/output_proposer.rs:508` (changes signature or replay validation logic)

Before
```rust
let result = build_proof_data(&proposal);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("unexpected ECDSA v-value"));
    }
```
After
```rust
let result = build_proof_data(&proposal);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("invalid ECDSA v-value"));
    }
```

## Snippet 3

Context: `crates/proof/tee/client/src/client_error.rs:18` (changes a sensitive control or state-update path)

Before
```rust
InvalidUrl(String),
}
```
After
```rust
InvalidUrl(String),
}

impl ClientError {
    /// Returns `true` if this error is transient and the operation can be retried.
    ///
    /// Only transport-level failures from the underlying jsonrpsee client are
    /// considered retryable. Configuration errors (`ClientCreation`, `InvalidUrl`)
```

## Snippet 4

Context: `crates/proof/tee/core/src/error.rs:23` (changes a sensitive control or state-update path)

Before
```rust
#[error("invalid signature length: expected 65 bytes, got {0}")]
    InvalidSignatureLength(usize),
}
```
After
```rust
#[error("invalid signature length: expected 65 bytes, got {0}")]
    InvalidSignatureLength(usize),

    /// Invalid ECDSA v-value.
    #[error("invalid ECDSA v-value: expected 0, 1, 27, or 28, got {0}")]
    InvalidVValue(u8),
}
```

# Fix Pattern

Centralize cryptographic payload encoding in a shared component and make malformed signature fields fail through explicit validation errors backed by regression tests.

## How It Was Fixed

The proposer stopped building the proof blob itself and now calls the shared `ProofEncoder`. The shared TEE core exposes an explicit invalid-`v` error, and the test suite now checks that a malformed recovery byte is rejected during proof construction.

# Why It Matters

1. Shared encoding reduces drift between callers in a sensitive proof-format path.

2. Explicit `v` validation makes malformed signatures fail earlier and more consistently.

3. The evidence supports validation hardening, not a confirmed exploit or bypass fix.

# Evidence Notes

Grounded evidence is limited to refactoring proof construction into `ProofEncoder`, adding `CryptoError::InvalidVValue(u8)`, and a regression test for `v=5`. The diff does not demonstrate replay prevention, signer-binding changes, proof forgery, or prior end-to-end acceptance of malformed proofs. Protocol security invariant: The proof blob sent toward verifier initialization should use the shared TEE proof format and reject structurally invalid signatures, including unsupported ECDSA recovery-byte (`v`) values, before forwarding. Verification notes: The patch does not prove that invalid signatures were previously accepted on-chain or by the enclave. The provided evidence does not show a replay, nonce, or signer-binding bug being fixed. No exploitability or proof-forgery scenario is demonstrated by the diff alone. The client retryability change is operational/error-handling context, not evidence of an authentication bypass fix. Validation tightening is directly supported by the changed error type and test expectation. Security relevance is plausible because the path handles proof/signature material. Exploitability and prior vulnerable behavior are not established by the provided snippets. The client retryability change is ancillary and not evidence of a security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-validation`
Final impact type: `malformed-input-acceptance`
Final confidence: `medium`
Final tags: `blockchain-core, tee, proof-encoding, signature-validation, cryptographic-input-validation`

The patch evidence supports a security-hardening classification, not a confirmed vulnerability fix. In a security-sensitive proof/signature path, the code stops doing ad hoc local proof-byte assembly and moves to a shared encoder that now explicitly rejects invalid ECDSA `v` values, with a regression test covering rejection of `v=5`. That is meaningful tightening of cryptographic input validation, but the supplied diff does not prove prior end-to-end acceptance of malformed proofs, replayability, forgery, or an exploitable bypass.

## Security Evidence

1. `build_proof_data()` now delegates to shared `ProofEncoder::encode_proof_bytes(...)` instead of manual local assembly.
2. `CryptoError::InvalidVValue(u8)` was added, showing explicit rejection of unsupported ECDSA recovery-byte values.
3. A regression test now asserts proof building fails when signature `v` is set to `5`.
4. The changed code sits in TEE proof construction and signature-format handling, which is a security-sensitive path.

## Missing Evidence

1. No patch snippet shows that invalid `v` values were previously accepted end-to-end.
2. No evidence demonstrates on-chain verifier, enclave, or downstream consumer behavior before the fix.
3. No exploit, replay, forgery, signer-confusion, or authorization-bypass scenario is shown.
4. The retryability/client error changes are operational and do not establish a security defect.

## Claim Boundaries

1. Supported claim: the commit hardens signature/proof encoding validation by rejecting invalid ECDSA `v` values in shared code.
2. Supported claim: the change reduces risk of malformed proof data being constructed or forwarded.
3. Not supported: a confirmed replay bug.
4. Not supported: a proven signature forgery or authentication bypass.
5. Not supported: prior vulnerable behavior beyond weaker or less centralized validation.
