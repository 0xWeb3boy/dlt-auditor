---
case_id: case_20251203_8924fbe38d
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
bug_class: input-validation
impact_type:
  - correctness-or-hardening
confidence: medium
source_quality: high
date: 2025-12-03
source_refs:
  - git:8924fbe38d1b8a92569b4043b89a12fc87a00a2b
  - "crates/protocol/derive/src/stages/batch/batch_stream.rs:194"
  - "crates/protocol/protocol/src/batch/span.rs:309"
  - "crates/protocol/protocol/src/batch/span.rs:396"
  - "crates/protocol/protocol/src/batch/span.rs:2208"
tags:
  - blockchain-core
  - consensus
  - input-validation
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a missing validation check and related error-handling gap in a consensus-sensitive batch-processing path. The evidence shows that overlapping span batches with an outdated L1 origin are now explicitly rejected, and singular-batch extraction failures are normalized to a flush-and-retry outcome. That supports a likely security-relevant protocol-validation fix, but not stronger claims about exploitability or observed impact.

## Observed Patch Facts

1. In `crates/protocol/derive/src/stages/batch/batch_stream.rs`, the patch replaces `self.get_single_batch(parent, l1_origins).map(Batch::Single)` with `match self.get_single_batch(parent, l1_origins) {`.

2. In `crates/protocol/protocol/src/batch/span.rs`, the patch replaces `.iter()` with `// Overlapping span batches can pass the prefix checks but then the`.

3. In `crates/protocol/protocol/src/batch/span.rs`, the patch replaces `if batch.timestamp <= l2_safe_head.block_info.timestamp {` with `let batch_timestamp = batch.timestamp;`.

4. In `crates/protocol/protocol/src/batch/span.rs`, the patch replaces `async fn test_check_batch_valid_with_genesis_epoch() {` with `async fn test_overlapped_blocks_origin_outdated() {`.

## Project Context

The changed code sits primarily in `crates/protocol/derive/src/stages/batch`, `crates/protocol/derive/src/stages`, `crates/protocol/protocol/src/batch`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/protocol/derive/src/stages/batch/batch_validator.rs`, `crates/protocol/derive/src/stages/batch/batch_queue.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/protocol/protocol/src/batch/inclusion.rs`, `crates/protocol/derive/src/stages/batch/batch_validator.rs`. The strongest project-level identifiers around this patch are `batch`, `Batch::Single`, `tokio::test`, and `Default::default`.

## Before/After Behavior

Before the patch, the shown span-batch code skipped pre-safe-head entries and then proceeded into origin lookup and later validation without the newly added check that rejects a post-safe-head batch whose epoch is older than the safe head's L1 origin. In batch_stream.rs, singular-batch extraction errors were passed through directly by mapping get_single_batch into Batch::Single. After the patch, span.rs rejects batch.epoch_num values older than l2_safe_head.l1_origin.number in both get_singular_batches and check_batch, and batch_stream.rs converts extraction errors into a logged flush plus temporary NotEnoughData.

# Root Cause

The implementation under-enforced the safe-head L1-origin invariant for overlapping span batches and did not route extraction failures through the same recovery behavior used for dropped invalid batches.

## Walkthrough

1. In span.rs, get_singular_batches now checks whether a post-safe-head batch has an epoch older than the safe head's L1 origin and returns L1OriginBeforeSafeHead if so.

2. In the same file, check_batch adds the same outdated-origin condition during batch validity checking so the invalid case is rejected earlier in validation too.

3. In batch_stream.rs, the code no longer blindly maps get_single_batch into Batch::Single.

4. The extraction path now distinguishes success, temporary lack of data, and extraction failure.

5. On extraction failure, the stream logs the error, flushes internal state, and returns temporary NotEnoughData, matching the intended dropped-batch handling path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/protocol/protocol/src/batch/span.rs | 300 | rejects span-derived singular batches whose post-safe-head L1 origin predates the safe head |
| crates/protocol/protocol/src/batch/span.rs | 378 | applies the same outdated-origin invariant during batch validity checking for overlapping span batches |
| crates/protocol/derive/src/stages/batch/batch_stream.rs | 188 | maps singular-batch extraction errors into deterministic flush/retry handling instead of passing through inconsistent extraction failures |

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

Add the same protocol-invariant check at multiple entry points in the validation/extraction flow, then normalize exceptional extraction outcomes into one deterministic recovery path.

## How It Was Fixed

The fix adds an explicit guard against post-safe-head batches whose epoch predates the safe head's L1 origin in both singular-batch extraction and batch validity checking. It also changes singular-batch extraction handling so errors trigger logging, state flush, and temporary NotEnoughData instead of propagating directly.

# Why It Matters

1. Rejects overlapping span batches with an outdated L1 origin after the safe head.

2. Keeps validation and extraction behavior aligned for the same invalid condition.

3. Prevents raw extraction errors from escaping through a consensus-sensitive path.

4. The commit text shows this change was scoped to the post-Holocene BatchValidator path.

# Evidence Notes

Direct support comes from the new batch.epoch_num < l2_safe_head.l1_origin.number checks in span.rs, the new L1OriginBeforeSafeHead error path, the changed batch_stream.rs match that flushes on extraction error, and the added test for overlapped blocks with an outdated origin. The evidence supports a protocol-validation bug fix in a consensus-sensitive subsystem. It does not by itself prove a disclosed exploit, chain split, fund loss, or full subsystem coverage; the commit message explicitly says the older BatchQueue path was still TODO. Protocol security invariant: After the L2 safe head, a singular batch derived from a span batch must not use an L1 origin older than the safe head's L1 origin. If singular-batch extraction in that path fails, the pipeline should take the same drop-or-flush recovery path used for invalid span batches rather than propagating an inconsistent intermediate error. Verification notes: The patch does not by itself prove a remotely exploitable attack or show attacker prerequisites. The patch does not prove that a network fork, fund loss, or production incident actually occurred. The commit message says the older `BatchQueue` path was still TODO, so full subsystem coverage was not yet established here. The evidence supports a consensus/validation invariant fix, not a cryptographic break or authentication issue. A new test named test_overlapped_blocks_origin_outdated was added for the outdated-origin overlap case. The commit message says the older BatchQueue path was still not fixed in this change. The provided material does not include evidence of a real-world incident or attacker workflow. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final tags: `blockchain-core, consensus, input-validation, validator`

The patch materially tightens validation in a consensus-sensitive batch-processing path by rejecting overlapping span batches whose post-safe-head L1 origin is older than the safe head, and by normalizing extraction failures into a flush-and-retry path instead of propagating inconsistent errors. In blockchain validator logic, that is plausibly security relevant and worth retaining, but the patch alone does not prove a concrete exploitable vulnerability, incident, or complete remediation across all paths, so this is better classified as security hardening rather than a confirmed security fix.

## Security Evidence

1. Adds an explicit guard rejecting `batch.epoch_num < l2_safe_head.l1_origin.number` in span-batch extraction.
2. Adds the same outdated-origin check in `check_batch`, showing intentional enforcement of a protocol/validator invariant at multiple entry points.
3. Introduces a dedicated `L1OriginBeforeSafeHead` error path for invalid overlapping span batches.
4. Changes singular-batch extraction failures to log, flush state, and return temporary `NotEnoughData`, reducing inconsistent handling in validator flow.
5. Adds a test named `test_overlapped_blocks_origin_outdated`, reinforcing that the change targets invalid consensus input handling.

## Missing Evidence

1. No proof of real-world exploitability, attacker control, or production impact is provided.
2. No evidence shows a chain split, fund loss, denial of service, or other concrete security consequence.
3. The commit message says the older `BatchQueue` path was still TODO, so the patch was not yet full subsystem coverage.
4. The patch does not include an advisory, CVE, or explicit statement that a security vulnerability was fixed.

## Claim Boundaries

1. Supported claim: the commit hardens consensus/validator input validation for overlapping span batches with outdated L1 origins.
2. Supported claim: the commit improves recovery behavior for singular-batch extraction failures in the validator pipeline.
3. Not supported: a confirmed exploitable vulnerability with demonstrated attacker impact.
4. Not supported: complete remediation of all related code paths, since `BatchQueue` remained unfixed in this change.
