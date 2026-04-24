---
case_id: case_20251203_a8aa4c3839
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
source_quality: high
date: 2025-12-03
source_refs:
  - git:a8aa4c383938411cc09faea6a20657765bbbe801
  - "kona/crates/protocol/derive/src/stages/batch/batch_stream.rs:194"
  - "kona/crates/protocol/protocol/src/batch/span.rs:309"
  - "kona/crates/protocol/protocol/src/batch/span.rs:396"
  - "kona/crates/protocol/protocol/src/batch/span.rs:2208"
bug_class: improper-input-validation
impact_type:
  - invalid-batch-acceptance
confidence: medium
tags:
  - blockchain-core
  - consensus
  - validation
  - hardening
  - batch-processing
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit checks for outdated L1 origins in span-batch processing and changes singular-batch extraction error handling to flush state and return temporary `NotEnoughData`. The code supports a correctness fix in protocol batch validation/derivation, but the provided evidence does not establish a concrete security impact.

## Observed Patch Facts

1. In `kona/crates/protocol/derive/src/stages/batch/batch_stream.rs`, the patch replaces `self.get_single_batch(parent, l1_origins).map(Batch::Single)` with `match self.get_single_batch(parent, l1_origins) {`.

2. In `kona/crates/protocol/protocol/src/batch/span.rs`, the patch replaces `.iter()` with `// Overlapping span batches can pass the prefix checks but then the`.

3. In `kona/crates/protocol/protocol/src/batch/span.rs`, the patch replaces `if batch.timestamp <= l2_safe_head.block_info.timestamp {` with `let batch_timestamp = batch.timestamp;`.

4. In `kona/crates/protocol/protocol/src/batch/span.rs`, the patch replaces `async fn test_check_batch_valid_with_genesis_epoch() {` with `async fn test_overlapped_blocks_origin_outdated() {`.

## Project Context

The changed code sits primarily in `kona/crates/protocol/derive/src/stages/batch`, `kona/crates/protocol/derive/src/stages`, `kona/crates/protocol/protocol/src/batch`, which anchors the finding in the `consensus` area of the project. Historical context from `kona/crates/protocol/derive/src/stages/batch/batch_validator.rs`, `kona/crates/protocol/derive/src/stages/batch/batch_queue.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `kona/crates/protocol/protocol/src/batch/inclusion.rs`, `kona/crates/protocol/derive/src/stages/batch/batch_validator.rs`. The strongest project-level identifiers around this patch are `batch`, `Batch::Single`, `tokio::test`, and `Default::default`.

## Before/After Behavior

Before the patch, post-safe-head span-batch processing could continue without an explicit guard against `batch.epoch_num < l2_safe_head.l1_origin.number`, and `batch_stream` directly mapped `get_single_batch(...)` into `Batch::Single`. After the patch, `get_singular_batches` and `check_batch` explicitly reject outdated origins, while `batch_stream` distinguishes `Ok(Some(_))`, `Ok(None)`, and `Err(_)`, flushing state and returning temporary `NotEnoughData` on extraction error.

# Root Cause

Validation and recovery rules were under-enforced in the span-batch path: the code did not explicitly reject an outdated post-safe-head L1 origin in the shown locations, and extraction failures were not normalized into the same flush/retry handling used for invalid span-batch processing.

## Walkthrough

1. `SpanBatch::get_singular_batches` now returns `SpanBatchError::L1OriginBeforeSafeHead` when a post-safe-head batch has `epoch_num` older than the safe head's L1 origin.

2. `SpanBatch::check_batch` adds the same outdated-origin check during validation.

3. `batch_stream` replaces `self.get_single_batch(parent, l1_origins).map(Batch::Single)` with explicit handling for `Ok(Some(_))`, `Ok(None)`, and `Err(_)`.

4. On extraction error, the new code logs a warning, flushes internal state, and returns temporary `NotEnoughData`.

5. A new test covers the overlapped/outdated-origin case, showing the intended validator behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| kona/crates/protocol/protocol/src/batch/span.rs | 309 | Rejects derived singular batches when an overlapping span batch would place the first post-safe-head batch on an outdated L1 origin. |
| kona/crates/protocol/protocol/src/batch/span.rs | 378 | Rechecks the same outdated-origin invariant during span batch validation before accepting the batch stream. |
| kona/crates/protocol/derive/src/stages/batch/batch_stream.rs | 194 | Handles singular-batch extraction failure as flush plus temporary retry, aligning invalid extraction with dropped-batch semantics in the post-Holocene validator path. |

## Code Snippets

## Snippet 1

Context: `kona/crates/protocol/derive/src/stages/batch/batch_stream.rs:194` (changes a sensitive control or state-update path)

Before
```rust
// Attempt to pull a SingleBatch out of the SpanBatch.
        self.get_single_batch(parent, l1_origins).map(Batch::Single)
    }
}
```
After
```rust
// Attempt to pull a SingleBatch out of the SpanBatch.
        match self.get_single_batch(parent, l1_origins) {
            Ok(Some(single_batch)) => Ok(Batch::Single(single_batch)),
            Ok(None) => Err(PipelineError::NotEnoughData.temp()),
            Err(e) => {
                warn!(target: "batch_span", "Extracting singular batches from span batch failed: {}", e);
                // If singular batch extraction fails, it should be handled the same as a
```

## Snippet 2

Context: `kona/crates/protocol/protocol/src/batch/span.rs:309` (changes a consensus- or validator-sensitive branch)

Before
```rust
continue;
            }
            let origin_epoch_hash = l1_origins[origin_index..l1_origins.len()]
                .iter()
```
After
```rust
continue;
            }
            // Overlapping span batches can pass the prefix checks but then the
            // first batch after the safe head has an outdated L1 origin.
            if batch.epoch_num < l2_safe_head.l1_origin.number {
                return Err(SpanBatchError::L1OriginBeforeSafeHead);
            }
            let origin_epoch_hash = l1_origins[origin_index..l1_origins.len()]
```

## Snippet 3

Context: `kona/crates/protocol/protocol/src/batch/span.rs:396` (changes a consensus- or validator-sensitive branch)

Before
```rust
let mut origin_advanced = starting_epoch_num == parent_block.l1_origin.number + 1;
        for (i, batch) in self.batches.iter().enumerate() {
            if batch.timestamp <= l2_safe_head.block_info.timestamp {
                continue;
            }
            // Find the L1 origin for the batch.
            for (j, j_block) in l1_blocks.iter().enumerate().skip(origin_index) {
                if batch.epoch_num == j_block.number {
```
After
```rust
let mut origin_advanced = starting_epoch_num == parent_block.l1_origin.number + 1;
        for (i, batch) in self.batches.iter().enumerate() {
            let batch_timestamp = batch.timestamp;
            let batch_epoch = batch.epoch_num;

            if batch_timestamp <= l2_safe_head.block_info.timestamp {
                continue;
            }
```

## Snippet 4

Context: `kona/crates/protocol/protocol/src/batch/span.rs:2208` (changes signature or replay validation logic)

Before
```rust
}

    #[tokio::test]
    async fn test_check_batch_valid_with_genesis_epoch() {
```
After
```rust
}

    #[tokio::test]
    async fn test_overlapped_blocks_origin_outdated() {
        let trace_store: TraceStorage = Default::default();
        let layer = CollectingLayer::new(trace_store.clone());
        tracing_subscriber::Registry::default().with(layer).init();
```

# Fix Pattern

Add explicit invariant checks in validation/derivation paths and convert ambiguous extraction failures into controlled flush-and-retry handling.

## How It Was Fixed

The patch enforces the outdated-origin rule in both singular-batch extraction and batch validation, and it changes extraction failures from a simple propagated result into a warning plus `flush()` plus temporary retry signal.

# Why It Matters

1. It prevents accepting or continuing with batches that violate the shown origin-ordering rule.

2. It makes extraction failure handling explicit instead of leaving it on a generic result path.

3. It adds the same check in more than one relevant path, reducing reliance on a single guard.

4. The evidence still shows only a correctness/validation fix; security consequences are not demonstrated here.

# Evidence Notes

Grounded evidence is limited to three code changes and one added test: explicit `L1OriginBeforeSafeHead` checks in `span.rs`, and flush-plus-`NotEnoughData` handling in `batch_stream.rs`. The commit message references a fix, specs clarification, and incomplete coverage for legacy `BatchQueue`, but that does not by itself prove exploitability, attacker control, consensus failure in production, or other concrete security impact. Protocol security invariant: For post-safe-head processing, a singular batch derived from a span batch should not use an L1 origin older than the safe head's L1 origin, and singular-batch extraction failures should be handled as invalid/incomplete batch processing rather than a normal successful path. Verification notes: The patch does not prove a practical attacker-controlled exploit path beyond malformed or overlapping span batches reaching validation. It does not prove a live chain split, finalized-state corruption, or funds impact occurred. The commit text says legacy `BatchQueue` handling was still todo, so the fix coverage shown here is not complete for every derivation path. The evidence supports a consensus/validation invariant bug, but not the exact severity or reachability in deployed networks. The new checks are directly visible in both `get_singular_batches` and `check_batch`. The extraction error path now visibly logs, flushes, and returns temporary `NotEnoughData`. The added test supports the intended outdated-origin rejection behavior. The provided evidence does not verify severity, reachability, or real-world exploit conditions. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-input-validation`
Final impact type: `invalid-batch-acceptance`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, validation, hardening, batch-processing`

The patch clearly tightens validation and recovery behavior in consensus-sensitive batch-processing code: it rejects span batches whose post-safe-head L1 origin is outdated, applies that check in more than one validation path, and flushes state on singular-batch extraction errors instead of continuing on a generic path. That is enough to treat the change as security-relevant hardening for a validator/consensus subsystem. However, the patch alone does not prove a concrete exploitable vulnerability, production chain split, or other demonstrated security impact, so this should be retained as security-hardening rather than a confirmed security fix.

## Security Evidence

1. Adds an explicit `L1OriginBeforeSafeHead` rejection when `batch.epoch_num` is older than the safe head's L1 origin.
2. Applies the outdated-origin guard in both singular-batch extraction and batch validation paths, indicating an enforced consensus invariant.
3. Changes singular-batch extraction failure handling to log, flush internal state, and return temporary `NotEnoughData` rather than using the prior generic mapping path.
4. Adds a test for the overlapped/outdated-origin case, showing the intended invalid-batch rejection behavior.

## Missing Evidence

1. No proof that attacker-controlled input can practically reach this path in deployed conditions.
2. No proof of concrete exploit impact such as chain split, finalized-state corruption, or fund loss.
3. Commit text says legacy `BatchQueue` handling was still TODO, so full exposure and full remediation are not shown.
4. No advisory, incident report, or other evidence ties this patch to a disclosed vulnerability.

## Claim Boundaries

1. Supported: the commit hardens consensus-sensitive validation and error-handling for span-batch processing.
2. Supported: the patch prevents processing of batches with outdated L1 origins in the shown paths.
3. Not supported: a confirmed exploitable vulnerability or demonstrated real-world consensus failure.
4. Not supported: severity, reachability, or complete remediation across every derivation path.
