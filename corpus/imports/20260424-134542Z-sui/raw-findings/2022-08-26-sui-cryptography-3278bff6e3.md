---
case_id: case_20220826_3278bff6e3
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: cryptography
confidence: high
source_quality: high
date: 2022-08-26
source_refs:
  - git:3278bff6e3418d315272a728e8d03261f80c5ee5
  - "crates/sui-core/src/checkpoints/mod.rs:529"
  - "crates/sui-core/src/authority.rs:1829"
  - "crates/sui-types/src/error.rs:468"
  - "crates/sui-core/src/checkpoints/mod.rs:80"
bug_class: consensus-error-misclassification
impact_type:
  - consensus-liveness
  - state-integrity
tags:
  - blockchain-core
  - consensus
  - validator
  - error-handling
  - denial-of-service
  - state-integrity
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes security-relevant error misclassification in the Narwhal consensus handling path. The prior design used broad SuiError/FragmentInternalError classification to decide whether consensus execution should continue or stop. The commit explicitly states that malformed data from a malicious validator could be interpreted as a node failure and halt honest validators, while the opposite misclassification could allow advancement after an internal node failure.

## Observed Patch Facts

1. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `// Check structure is correct and signatures verify` with `// TODO: We should not schedule a cert if it has already been executed.`.

2. In `crates/sui-core/src/authority.rs`, the patch replaces `self.database.last_consensus_index()` with `self.database`.

3. In `crates/sui-types/src/error.rs`, the patch replaces `impl ExecutionStateError for SuiError {` with `type BoxError = Box<dyn std::error::Error + Send + Sync + 'static>;`.

4. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `#[derive(Debug, Error)]` with `/// DBMap tables for checkpoints`.

## Project Context

The changed code sits primarily in `crates/sui-core/src/checkpoints`, `crates/sui-core/src`, `crates/sui-core`, which anchors the finding in the `cryptography` area of the project. Historical context from `crates/sui-types/src/waypoint.rs`, `crates/sui-types/src/messages_checkpoint.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/waypoint.rs`, `crates/sui-types/src/messages_checkpoint.rs`. The strongest project-level identifiers around this patch are `Error`, `error`, `FragmentInternalError::Error`, and `fragment`. Nearby tests or test-like files include `crates/sui-core/src/epoch/tests/reconfiguration_tests.rs`, `crates/sui-core/src/checkpoints/tests/checkpoint_tests.rs`.

## Before/After Behavior

Before the patch, checkpoint fragment verification errors were mapped through FragmentInternalError::Error, and generic ExecutionStateError implementations over FragmentInternalError and SuiError drove the node-error decision, including broad matching of SuiError variants such as ObjectFetchFailed, ByzantineAuthoritySuspicion, StorageError, and GenericAuthorityError. After the patch, the generic SuiError and FragmentInternalError node-error classifiers are removed from the shown path, NarwhalHandlerError is introduced with explicit NodeError and input-verification categories, and database consensus-index loading failures are explicitly mapped to NarwhalHandlerError::NodeError.

# Root Cause

The root cause was ambiguous error classification at the consensus execution boundary. The handler inferred whether to continue or stop from coarse underlying Sui error types instead of explicitly tracking whether the failure came from untrusted consensus input or from local node/state processing.

## Walkthrough

1. Narwhal delivers consensus data into Sui's execution/checkpoint handling path.

2. The handler must decide whether an error means the incoming data is invalid and can be skipped, or whether the local node may have failed and should stop consuming the stream.

3. Before the fix, fragment verification failure was mapped into FragmentInternalError::Error in the shown checkpoint path.

4. The code also had generic ExecutionStateError implementations for FragmentInternalError and SuiError, making continuation decisions depend on broad error-type matching.

5. The commit states that a malicious validator could send incorrect data that would be interpreted as a node failure, preventing honest validators from proceeding.

6. The commit also states that the inverse classification error could allow continuation after a true node error, risking incomplete local state.

7. The patch removes the shown generic classifiers and introduces NarwhalHandlerError with explicit categories for local node errors and rejected Narwhal transaction/input verification failures.

8. The load_execution_indices path now maps database/index loading errors directly to NarwhalHandlerError::NodeError, preserving stop-on-local-state-error behavior without relying on generic SuiError matching.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/authority.rs | 1829 | Narwhal ExecutionState integration maps local database/index loading failures explicitly to NodeError, preserving the stop-on-local-error behavior. |
| crates/sui-core/src/checkpoints/mod.rs | 509 | Checkpoint fragment handling path schedules certificates from consensus fragments after the verification/processing split, avoiding conflation of invalid input with internal processing failure. |
| crates/sui-core/src/checkpoints/mod.rs | 80 | Old FragmentInternalError abstraction is removed from the checkpoint consensus path, eliminating an imprecise wrapper used for downstream node_error classification. |
| crates/sui-types/src/error.rs | 468 | Generic ExecutionStateError implementation for SuiError is removed, ending broad error-type matching as the basis for consensus continuation decisions. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/checkpoints/mod.rs:529` (changes signature or replay validation logic)

Before
```rust
}

        // Check structure is correct and signatures verify
        fragment
            .verify(committee)
            .map_err(FragmentInternalError::Error)?;

        // Schedule for execution all the certificates that are included here.
```
After
```rust
}

        // Schedule for execution all the certificates that are included here.
        // TODO: We should not schedule a cert if it has already been executed.
        handle_pending_cert.add_pending_certificates(
            fragment
                .certs
                .iter()
```

## Snippet 2

Context: `crates/sui-core/src/authority.rs:1829` (changes bounds, limits, or capacity handling)

Before
```rust
async fn load_execution_indices(&self) -> Result<ExecutionIndices, Self::Error> {
        self.database.last_consensus_index()
    }
}

impl ExecutionStateError for FragmentInternalError {
    fn node_error(&self) -> bool {
```
After
```rust
async fn load_execution_indices(&self) -> Result<ExecutionIndices, Self::Error> {
        self.database
            .last_consensus_index()
            .map_err(NarwhalHandlerError::NodeError)
    }
}
```

## Snippet 3

Context: `crates/sui-types/src/error.rs:468` (changes a sensitive control or state-update path)

Before
```rust
}

impl ExecutionStateError for SuiError {
    fn node_error(&self) -> bool {
        matches!(
            self,
            Self::ObjectFetchFailed { .. }
                | Self::ByzantineAuthoritySuspicion { .. }
```
After
```rust
}

type BoxError = Box<dyn std::error::Error + Send + Sync + 'static>;
```

## Snippet 4

Context: `crates/sui-core/src/checkpoints/mod.rs:80` (changes bounds, limits, or capacity handling)

Before
```rust
}

#[derive(Debug, Error)]
pub enum FragmentInternalError {
    #[error("Sui error: {0}")]
    Error(SuiError),
    #[error("Error processing fragment, retrying")]
    Retry(Box<CheckpointFragment>),
```
After
```rust
}

/// DBMap tables for checkpoints
#[derive(DBMapUtils)]
```

# Fix Pattern

Replace broad type-based error classification in consensus handling with explicit domain-specific error variants that encode whether a failure came from untrusted input verification or local node processing.

## How It Was Fixed

The patch removes the old generic ExecutionStateError classification for SuiError and removes FragmentInternalError from the shown checkpoint consensus path. It introduces NarwhalHandlerError with explicit comments separating local node errors from Narwhal transaction verification failures, and maps local database/index loading failures to NarwhalHandlerError::NodeError. The commit describes this as separating input verification from processing.

# Why It Matters

1. Malformed validator-provided input should not be able to halt honest validators by being misclassified as a local node failure.

2. Local node or storage failures should not be skipped as if they were merely bad input, because state may be incomplete.

3. The evidence supports consensus liveness and state-safety impact, not theft, signature forgery, or a cryptographic primitive flaw.

4. The attacker model supported by the provided evidence is a malicious validator, not an arbitrary unauthenticated remote user.

# Evidence Notes

The strongest evidence is the commit message, which explicitly describes the dangerous misclassification and malicious-validator liveness scenario. Code evidence shows removal of FragmentInternalError from the shown checkpoint path, removal of ExecutionStateError for SuiError, addition of NarwhalHandlerError with explicit NodeError and input-verification categories, and explicit mapping of last_consensus_index failures to NarwhalHandlerError::NodeError. The provided hunks do not show the full new verification path or a complete exploit trace, so claims should stay limited to error-classification, consensus liveness, and state-safety risk. Protocol security invariant: The Narwhal/Sui consensus execution handler must classify failures by source: invalid validator-provided consensus input should be rejected or skipped so the stream can continue, while local node, storage, or state-processing failures must stop advancement because local state may be incomplete. Verification notes: The patch does not prove unauthenticated remote exploitability; the described actor is a malicious validator sending incorrect consensus data. The evidence supports potential consensus liveness failure and state-safety risk, not theft, signature forgery, or cryptographic breakage. The patch does not show a full end-to-end exploit trace or quantify how many validators must receive the malformed data. The incomplete-state scenario is described by the commit rationale, but the provided hunks do not demonstrate a specific corrupted object or checkpoint outcome. Supported by commit rationale and focused changes in authority.rs, checkpoints/mod.rs, and error.rs. No evidence of cryptographic primitive breakage or signature forgery. No evidence of direct asset theft or arbitrary remote exploitability. Incomplete-state impact is stated by the commit but not demonstrated with a concrete corrupted object or checkpoint in the provided hunks. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `consensus-error-misclassification`
Final impact type: `consensus-liveness, state-integrity`
Final tags: `blockchain-core, consensus, validator, error-handling, denial-of-service, state-integrity`

The supplied commit message explicitly describes a malicious-validator scenario where incorrect consensus input could be misclassified as a local node failure and halt honest validators, with the inverse risking advancement after an internal state error. The patch evidence supports a targeted change from broad SuiError/FragmentInternalError node-error classification toward explicit NarwhalHandlerError categories. This is security-relevant consensus error handling, but the corpus metadata should avoid overclaiming cryptography, signature, or concrete state-corruption details.

## Security Evidence

1. Commit message names malicious validator input causing honest validators to stop consensus progress.
2. Patch introduces explicit NarwhalHandlerError categories separating local node errors from rejected Narwhal transaction/input verification failures.
3. Database consensus-index load failures are explicitly mapped to NodeError, preserving stop-on-local-state-error behavior.
4. Generic ExecutionStateError classification for SuiError and FragmentInternalError is removed from the shown paths.

## Missing Evidence

1. No full end-to-end exploit trace is provided.
2. The provided hunks do not show the complete new input verification path.
3. No concrete corrupted object, checkpoint, or finalized invalid state outcome is demonstrated.
4. No evidence supports cryptographic primitive breakage or signature forgery.

## Claim Boundaries

1. Supported attacker model is a malicious validator or consensus participant, not arbitrary unauthenticated remote users.
2. Supported impact is consensus liveness denial of service and possible state-safety risk from misclassified local errors.
3. Do not classify this as a cryptography or signature-validation flaw based on the supplied evidence.
4. Do not claim theft, asset loss, or proven state corruption from the provided patch alone.
