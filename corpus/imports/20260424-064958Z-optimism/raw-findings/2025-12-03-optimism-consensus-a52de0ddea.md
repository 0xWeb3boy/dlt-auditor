---
case_id: case_20251203_a52de0ddea
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
  - git:a52de0ddea8396a46cdacc40ac6e0316f9577c48
  - "crates/protocol/derive/src/stages/batch/batch_stream.rs:194"
  - "crates/protocol/protocol/src/batch/span.rs:309"
  - "crates/protocol/protocol/src/batch/span.rs:396"
  - "crates/protocol/protocol/src/batch/span.rs:2208"
bug_class: consensus-invariant-enforcement
impact_type:
  - consensus-integrity-risk
confidence: medium
tags:
  - blockchain-core
  - consensus
  - validator
  - invariant-check
  - state-recovery
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit checks for an outdated L1 origin in overlapped span-batch handling and changes singular-batch extraction failures to flush state and return temporary backpressure. The evidence supports a protocol-correctness fix in validator/derivation logic, but it does not by itself establish an exploitable security vulnerability.

## Observed Patch Facts

1. In `crates/protocol/derive/src/stages/batch/batch_stream.rs`, the patch replaces `self.get_single_batch(parent, l1_origins).map(Batch::Single)` with `match self.get_single_batch(parent, l1_origins) {`.

2. In `crates/protocol/protocol/src/batch/span.rs`, the patch replaces `.iter()` with `// Overlapping span batches can pass the prefix checks but then the`.

3. In `crates/protocol/protocol/src/batch/span.rs`, the patch replaces `if batch.timestamp <= l2_safe_head.block_info.timestamp {` with `let batch_timestamp = batch.timestamp;`.

4. In `crates/protocol/protocol/src/batch/span.rs`, the patch replaces `async fn test_check_batch_valid_with_genesis_epoch() {` with `async fn test_overlapped_blocks_origin_outdated() {`.

## Project Context

The changed code sits primarily in `crates/protocol/derive/src/stages/batch`, `crates/protocol/derive/src/stages`, `crates/protocol/protocol/src/batch`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/protocol/derive/src/stages/batch/batch_validator.rs`, `crates/protocol/derive/src/stages/batch/batch_queue.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/protocol/protocol/src/batch/inclusion.rs`, `crates/protocol/derive/src/stages/batch/batch_validator.rs`. The strongest project-level identifiers around this patch are `batch`, `Batch::Single`, `tokio::test`, and `Default::default`.

## Before/After Behavior

Before the patch, overlapped span-batch processing could reach origin lookup and validation without an explicit `batch.epoch_num < l2_safe_head.l1_origin.number` check, and singular-batch extraction errors were propagated directly from `.map(Batch::Single)`. After the patch, both extraction and validation paths reject batches with an origin older than the safe head, and extraction errors cause a warning, `flush()`, and temporary `NotEnoughData` handling.

# Root Cause

The changed code indicates missing invariant enforcement for post-safe-head span-batch overlap cases, plus weaker local recovery when singular-batch extraction failed.

## Walkthrough

1. `SpanBatch::get_singular_batches` now returns `SpanBatchError::L1OriginBeforeSafeHead` when a post-safe-head batch has an older L1 origin number than the safe head.

2. `SpanBatch::check_batch` adds the same outdated-origin check in the overlap-handling path.

3. The new comments say overlapping span batches could pass prefix checks yet still have the first post-safe-head batch use an outdated L1 origin.

4. `batch_stream.rs` stops using direct `.map(Batch::Single)` conversion and instead distinguishes `Ok(Some(_))`, `Ok(None)`, and `Err(_)`.

5. On extraction error, the stream logs, flushes internal state, and returns temporary `PipelineError::NotEnoughData`.

6. A new test named `test_overlapped_blocks_origin_outdated` was added, which supports the intended scenario.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/protocol/protocol/src/batch/span.rs | 300 | singular-batch extraction now rejects span batches whose first post-safe-head batch has an outdated L1 origin |
| crates/protocol/protocol/src/batch/span.rs | 378 | batch validity check now enforces the same no-outdated-origin rule during overlap handling |
| crates/protocol/derive/src/stages/batch/batch_stream.rs | 194 | derivation pipeline now flushes span-batch state and converts extraction errors into temporary pipeline backpressure instead of propagating inconsistent extraction results |

## Code Snippets

## Snippet 1

Context: `crates/protocol/derive/src/stages/batch/batch_stream.rs:194` (changes a sensitive control or state-update path)

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

Context: `crates/protocol/protocol/src/batch/span.rs:309` (changes a consensus- or validator-sensitive branch)

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

Context: `crates/protocol/protocol/src/batch/span.rs:396` (changes a consensus- or validator-sensitive branch)

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

Context: `crates/protocol/protocol/src/batch/span.rs:2208` (changes signature or replay validation logic)

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

Add explicit invariant checks in both validation and extraction paths, and convert extraction failures into a safe reset/retry path.

## How It Was Fixed

The fix adds an explicit outdated-origin guard in `span.rs` in both singular-batch extraction and batch validation. It also changes `batch_stream.rs` so extraction failures are handled like a dropped span batch by flushing buffered state and returning temporary backpressure instead of continuing with the current span-batch state.

# Why It Matters

1. It closes a specific gap in overlap handling for span batches after the safe head.

2. It makes validation and extraction enforce the same outdated-origin rule.

3. It avoids continuing derivation with span-batch state after extraction failure.

4. The commit body itself says coverage is incomplete because the old `BatchQueue` path was still pending.

# Evidence Notes

The strongest support is the added `batch.epoch_num < l2_safe_head.l1_origin.number` checks in two `span.rs` paths, the new flush-on-extraction-error behavior in `batch_stream.rs`, and the added overlap-focused test. The evidence supports a correctness/invariant fix in consensus-sensitive code, but it does not prove real-world exploitability, impact, or that pre-fix behavior necessarily led to unsafe acceptance in all cases. Protocol security invariant: After the L2 safe head, a span batch should not yield or validate a singular batch whose L1 origin number is older than the safe head's L1 origin; if extraction fails, the derivation path should discard that span-batch state rather than continue with ambiguous state. Verification notes: The patch does not prove a practical chain split or attacker-triggerable exploit from the provided evidence alone. The patch does not establish fund loss, key compromise, or cryptographic breakage. The commit body says the old `BatchQueue` path was still todo, so the evidence only confirms the post-Holocene `BatchValidator` path. The patch does not show whether the pre-fix behavior caused unsafe acceptance, liveness failure, or both in all cases. No full diff or runtime reproduction was provided. The evidence is limited to selected hunks plus commit text. The commit body says only the post-Holocene `BatchValidator` path was fixed so far. Security impact is therefore plausible but not established from the provided evidence alone. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-invariant-enforcement`
Final impact type: `consensus-integrity-risk`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, validator, invariant-check, state-recovery`

The patch clearly tightens behavior in a consensus-sensitive validation/derivation path by rejecting span batches whose post-safe-head entries carry an outdated L1 origin and by flushing state on extraction failure. That is meaningful security hardening for blockchain-core code because it narrows acceptance of malformed or inconsistent batch state. However, the provided evidence does not prove a concrete exploitable vulnerability, chain split, or other realized security impact before the fix.

## Security Evidence

1. Adds an explicit outdated-origin rejection when extracting singular batches after the safe head.
2. Adds the same outdated-origin guard in batch validation, aligning validation and extraction behavior.
3. Changes extraction failure handling to warn, flush buffered state, and return temporary backpressure rather than continue with ambiguous span-batch state.
4. Introduces a targeted test for overlapped blocks with an outdated origin, showing the risky condition was intentional and relevant.

## Missing Evidence

1. No proof that pre-fix behavior was attacker-triggerable in a deployed setting.
2. No direct evidence of concrete exploitation such as invalid block acceptance, chain split, or fund impact.
3. Commit text says the older `BatchQueue` path was still pending, so the fix was not complete across all paths.

## Claim Boundaries

1. Supported: this commit hardens consensus/validator logic against outdated-origin overlap handling and unsafe recovery behavior.
2. Not supported: this commit alone proves a concrete exploitable consensus vulnerability existed.
3. Not supported: all affected derivation paths were fixed by this commit.
