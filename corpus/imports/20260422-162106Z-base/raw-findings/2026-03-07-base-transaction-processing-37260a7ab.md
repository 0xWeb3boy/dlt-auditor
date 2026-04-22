---
case_id: case_20260307_37260a7ab
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
  - git:37260a7ab212945dbc26ddec90642c976db10e3e
  - "crates/proof/proposer/src/output_proposer.rs:59"
  - "crates/proof/proposer/src/output_proposer.rs:508"
  - "crates/proof/tee/client/src/client_error.rs:18"
  - "crates/proof/tee/core/src/error.rs:23"
bug_class: signature-validation-hardening
impact_type:
  - malformed-input-rejection
confidence: medium
tags:
  - ecdsa
  - signature-validation
  - proof-encoding
  - hardening
  - cryptographic-boundary
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a narrow conclusion: proof-byte construction and signature-shape checks were centralized into a shared encoder, and invalid ECDSA `v` values are now rejected explicitly. That is a real validation improvement on a sensitive path, but the supplied excerpts do not show that malformed signatures were previously accepted by the verifier, accepted on-chain, or usable to bypass authorization. This should be treated as security-relevant hardening at most, with the vulnerability thesis unproven.

## Observed Patch Facts

1. In `crates/proof/proposer/src/output_proposer.rs`, the patch replaces `let sig = &proposal.output.signature;` with `ProofEncoder::encode_proof_bytes(`.

2. In `crates/proof/proposer/src/output_proposer.rs`, the patch replaces `assert!(result.unwrap_err().to_string().contains("unexpected ECDSA v-value"));` with `assert!(result.unwrap_err().to_string().contains("invalid ECDSA v-value"));`.

3. In `crates/proof/tee/client/src/client_error.rs`, the patch adds `impl ClientError {`.

4. In `crates/proof/tee/core/src/error.rs`, the patch adds `/// Invalid ECDSA v-value.`.

## Project Context

The changed code sits primarily in `crates/proof/proposer/src`, `crates/proof/proposer`, `crates/proof/tee/client/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/proof/tee/core/src/proof.rs`, `crates/proof/tee/core/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/proof/proposer/src/prover/mod.rs`, `crates/proof/proposer/src/driver/mod.rs`. The strongest project-level identifiers around this patch are `ProposerError::Internal`, `proposal`, `result`, and `value`.

## Before/After Behavior

Before the change, `build_proof_data()` in the proposer assembled proof bytes locally and the visible guard only checked signature length before writing fields into the output buffer. After the change, the proposer delegates proof construction to `ProofEncoder::encode_proof_bytes(...)`, `CryptoError` includes `InvalidVValue(u8)`, and the test now expects rejection for a signature whose final byte is an invalid `v` value. The observed behavior change is stricter local validation and centralization of encoding logic, not demonstrated prevention of a proven exploit.

# Root Cause

The grounded root cause is fragmented proof encoding with incomplete explicit validation at the proposer-side serialization boundary. The evidence only shows that length checks were visible locally before, while `v` validation became explicit after the shared encoder change; it does not show how downstream components handled malformed proof data previously.

## Walkthrough

1. `build_proof_data()` is the visible proposer entry point for constructing bytes used by `AggregateVerifier.initialize()`.

2. The pre-change excerpt shows manual assembly of the proof payload and an explicit check for signature length only.

3. The post-change excerpt replaces that local assembly with `ProofEncoder::encode_proof_bytes(...)`, indicating the encoding logic moved into shared code.

4. `crates/proof/tee/core/src/error.rs` adds `CryptoError::InvalidVValue(u8)` with accepted values `0`, `1`, `27`, and `28`, which is direct evidence of a newly explicit validation rule.

5. The updated proposer test mutates `sig[64] = 5` and now expects an error containing `invalid ECDSA v-value`, confirming the intended rejection behavior at proof construction time.

6. `client_error.rs` retry classification is operational support code and does not strengthen the security claim from the provided evidence.

7. What is not shown is equally important: no excerpt demonstrates prior acceptance by the verifier, a signature-verification bypass, replay, privilege gain, or any exploitable state transition.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/proof/proposer/src/output_proposer.rs | 46 | Builds proof data for `AggregateVerifier.initialize()` on the proposer path; now delegates to shared `ProofEncoder` instead of local manual encoding. |
| crates/proof/tee/core/src/proof.rs | 1 | Shared proof encoding logic and constants for TEE proofs; likely the canonical enforcement point for signature length and `v` normalization/validation. |
| crates/proof/tee/core/src/error.rs | 17 | Introduces explicit cryptographic error for invalid ECDSA `v` values, showing the concrete validation rule added by the patch. |

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

Centralize serialization of sensitive payloads into a shared encoder and make malformed cryptographic inputs fail early with dedicated error types.

## How It Was Fixed

The patch moved proposer-side proof-byte construction into shared `ProofEncoder` code, re-exported the encoder and related constants from TEE core, and added an explicit invalid-`v` error path that the proposer test now exercises. The practical fix is stronger and more centralized input validation during proof encoding.

# Why It Matters

1. Shared encoding reduces divergence between components that prepare the same proof format.

2. Explicit `v` validation makes malformed signatures fail earlier and more predictably.

3. The change improves robustness on a cryptographic boundary even though exploitability is not established from the excerpts.

# Evidence Notes

The strongest evidence is the combination of three facts: local proof assembly was replaced with `ProofEncoder::encode_proof_bytes(...)`; `CryptoError` gained `InvalidVValue(u8)` with a concrete accepted set; and a test now asserts rejection when `sig[64]` is invalid. That supports a claim of stricter signature-format validation. It does not support stronger claims such as replay prevention, on-chain acceptance of bad signatures before the patch, signer forgery, or a full signature-verification bypass. Because the security consequence is inferred rather than demonstrated, the security verdict should be downgraded to `unclear`. Protocol security invariant: Proof bytes sent on the proposer-to-verifier path should be encoded in one canonical format, with a 65-byte signature and an allowed ECDSA recovery byte value. The provided evidence shows that this invariant is now enforced more explicitly at the encoding boundary, but it does not establish that the prior code violated a security guarantee in an exploitable way. Verification notes: The patch does not prove that invalid signatures were previously accepted on-chain. The patch does not establish a replay vulnerability or replay fix by itself. The patch does not show compromise of enclave keys, signer identity, or signature verification logic. The `EnclaveProvider` abstraction and client retry changes look architectural/operational, not independently security-relevant from the shown evidence. Exploitability is not demonstrated by the provided diff excerpts. Grounded by direct diff evidence showing new explicit invalid-`v` handling. No evidence provided for exploit reproduction or prior verifier acceptance of malformed proofs. No evidence provided for replay, authorization bypass, or key-compromise impact. Best classification from the supplied excerpts is validation hardening with unproven vulnerability status. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `signature-validation-hardening`
Final impact type: `malformed-input-rejection`
Final confidence: `medium`
Final tags: `ecdsa, signature-validation, proof-encoding, hardening, cryptographic-boundary`

The supplied patch evidence supports a conservative hardening conclusion, not a proven vulnerability fix. The change moves proof-byte construction into a shared encoder, adds an explicit `InvalidVValue` error for ECDSA recovery-byte validation, and updates a test to require rejection of an invalid `v` value. That is a meaningful tightening on a security-sensitive proof/signature path, but the excerpts do not show prior verifier acceptance, authorization bypass, replay, or any demonstrated exploit. This belongs in the corpus as security hardening only.

## Security Evidence

1. `build_proof_data()` now delegates to shared `ProofEncoder::encode_proof_bytes(...)` instead of local manual assembly.
2. `CryptoError` gains `InvalidVValue(u8)` with an explicit allowed set `0, 1, 27, 28`.
3. A test now asserts that a signature with `sig[64] = 5` is rejected.
4. The changed path constructs proof bytes used for verifier initialization, so the validation sits on a cryptographic boundary.

## Missing Evidence

1. No excerpt shows malformed signatures were previously accepted by the verifier or on-chain.
2. No evidence demonstrates replay, forgery, privilege gain, or signature-verification bypass.
3. No exploit reproduction, incident report, or security-oriented commit message is provided.
4. The retry-classification change in `client_error.rs` does not materially strengthen the security claim.

## Claim Boundaries

1. Supported claim: the patch adds stricter signature-shape validation and centralizes proof encoding.
2. Supported claim: invalid ECDSA `v` values are now explicitly rejected during proof construction.
3. Not supported: this commit fixes a confirmed exploitable vulnerability.
4. Not supported: the change proves replay prevention, request forgery prevention, or prior authorization bypass.
