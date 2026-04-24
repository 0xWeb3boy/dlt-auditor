---
case_id: case_20260304_d8de8afa9
project: reth
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
bug_class: resource-exhaustion
confidence: low
source_quality: high
date: 2026-03-04
source_refs:
  - git:d8de8afa95aed287ad5fcab7d49cbf92e4131ade
  - "crates/stages/stages/src/stages/hashing_storage.rs:100"
  - "crates/stages/stages/src/stages/hashing_account.rs:170"
  - "crates/stages/stages/src/stages/hashing_account.rs:14"
  - "crates/stages/stages/src/stages/hashing_storage.rs:13"
impact_type:
  - availability
tags:
  - infrastructure
  - storage
  - resource-exhaustion
  - availability
  - memory-bounding
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied diff supports a memory-bounding change in the account and storage hashing stages: the clean-versus-incremental decision now uses the total remaining range instead of only the next batch window. That is consistent with availability hardening, but the provided evidence does not establish a concrete vulnerability, exploit path, or security impact beyond improved resource control.

## Observed Patch Facts

1. In `crates/stages/stages/src/stages/hashing_storage.rs`, the patch replaces `let (from_block, to_block) = input.next_block_range().into_inner();` with `// Use the total remaining range to decide clean vs incremental.`.

2. In `crates/stages/stages/src/stages/hashing_account.rs`, the patch replaces `let (from_block, to_block) = input.next_block_range().into_inner();` with `// Use the total remaining range to decide clean vs incremental.`.

3. In `crates/stages/stages/src/stages/hashing_account.rs`, the patch replaces `AccountHashingCheckpoint, EntitiesCheckpoint, ExecInput, ExecOutput, Stage, StageChec...` with `AccountHashingCheckpoint, BlockRangeOutput, EntitiesCheckpoint, ExecInput, ExecOutput...`.

4. In `crates/stages/stages/src/stages/hashing_storage.rs`, the patch replaces `EntitiesCheckpoint, ExecInput, ExecOutput, Stage, StageCheckpoint, StageError, StageId,` with `BlockRangeOutput, EntitiesCheckpoint, ExecInput, ExecOutput, Stage, StageCheckpoint,`.

## Project Context

The changed code sits primarily in `crates/stages/stages/src/stages`, `crates/stages/stages/src`, which anchors the finding in the `storage` area of the project. Historical context from `crates/stages/stages/src/stages/bodies.rs`, `crates/stages/stages/src/stages/merkle.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/stages/stages/src/stages/bodies.rs`, `crates/stages/stages/src/stages/merkle.rs`. The strongest project-level identifiers around this patch are `from_block`, `input`, `reth_storage_errors::provider::ProviderResult`, and `hash`.

## Before/After Behavior

Before the patch, both hashing stages unpacked `(from_block, to_block)` from `input.next_block_range().into_inner()` and compared `to_block - from_block` with `self.clean_threshold`, so the decision was based on the size of the next batch. After the patch, both stages compute `total_range = input.target() - input.checkpoint().block_number`, keep `from_block = input.next_block()`, and compare `total_range` with the threshold instead. The practical change is that a large outstanding backlog is now more likely to trigger the clean/full-rehash path even when the immediate scheduled window is small.

# Root Cause

The selection heuristic for clean versus incremental hashing was tied to the next scheduled block window rather than the full remaining work. As a result, a large backlog could still be processed as many small incremental windows, undermining the intended memory bound for the stage.

## Walkthrough

1. In `crates/stages/stages/src/stages/hashing_storage.rs`, the old execute path derived `(from_block, to_block)` from `input.next_block_range().into_inner()` before deciding between clean and incremental hashing.

2. That file now comments that it will use the total remaining range, computes `total_range = input.target() - input.checkpoint().block_number`, and keeps `from_block = input.next_block()`.

3. The storage-stage threshold check changed from comparing `to_block - from_block` against `self.clean_threshold` to comparing `total_range` against the same threshold.

4. `crates/stages/stages/src/stages/hashing_account.rs` applies the same change in its execute path, replacing the per-batch comparison with a total-remaining-range comparison.

5. The import additions such as `BlockRangeOutput` appear supportive of the refactor around range handling, but the clearest behavioral evidence is the changed threshold condition in the two execute paths.

6. The evidence shows improved resource-selection logic in a sensitive pipeline stage, but it does not by itself prove state corruption, consensus failure, remote triggerability, or a demonstrable exploit scenario.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/stages/stages/src/stages/hashing_storage.rs | 90 | storage hashing stage execute path; selects clean full rehash vs incremental changeset-based hashing |
| crates/stages/stages/src/stages/hashing_account.rs | 161 | account hashing stage execute path; selects clean full rehash vs incremental changeset-based hashing |
| crates/stages/stages/src/stages/hashing_storage.rs | 100 | threshold condition changed from per-batch range to total remaining range |
| crates/stages/stages/src/stages/hashing_account.rs | 170 | threshold condition changed from per-batch range to total remaining range |

## Code Snippets

## Snippet 1

Context: `crates/stages/stages/src/stages/hashing_storage.rs:100` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

        let (from_block, to_block) = input.next_block_range().into_inner();

        // if there are more blocks then threshold it is faster to go over Plain state and hash all
        // account otherwise take changesets aggregate the sets and apply hashing to
        // AccountHashing table. Also, if we start from genesis, we need to hash from scratch, as
        // genesis accounts are not in changeset, along with their storages.
```
After
```rust
}

        // Use the total remaining range to decide clean vs incremental.
        let total_range = input.target() - input.checkpoint().block_number;
        let from_block = input.next_block();

        if total_range > self.clean_threshold || from_block == 1 {
            // if there are more blocks than threshold it is faster to go over Plain state and
```

## Snippet 2

Context: `crates/stages/stages/src/stages/hashing_account.rs:170` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

        let (from_block, to_block) = input.next_block_range().into_inner();

        // if there are more blocks then threshold it is faster to go over Plain state and hash all
        // account otherwise take changesets aggregate the sets and apply hashing to
        // AccountHashing table. Also, if we start from genesis, we need to hash from scratch, as
        // genesis accounts are not in changeset.
```
After
```rust
}

        // Use the total remaining range to decide clean vs incremental.
        let total_range = input.target() - input.checkpoint().block_number;
        let from_block = input.next_block();

        if total_range > self.clean_threshold || from_block == 1 {
            // if there are more blocks than threshold it is faster to go over Plain state and
```

## Snippet 3

Context: `crates/stages/stages/src/stages/hashing_account.rs:14` (changes a sensitive control or state-update path)

Before
```rust
};
use reth_stages_api::{
    AccountHashingCheckpoint, EntitiesCheckpoint, ExecInput, ExecOutput, Stage, StageCheckpoint,
    StageError, StageId, UnwindInput, UnwindOutput,
};
use reth_storage_errors::provider::ProviderResult;
use std::{
    fmt::Debug,
```
After
```rust
};
use reth_stages_api::{
    AccountHashingCheckpoint, BlockRangeOutput, EntitiesCheckpoint, ExecInput, ExecOutput, Stage,
    StageCheckpoint, StageError, StageId, UnwindInput, UnwindOutput,
};
use reth_storage_errors::provider::ProviderResult;
use std::{
    collections::BTreeSet,
```

## Snippet 4

Context: `crates/stages/stages/src/stages/hashing_storage.rs:13` (changes a sensitive control or state-update path)

Before
```rust
use reth_provider::{DBProvider, HashingWriter, StatsReader, StorageReader};
use reth_stages_api::{
    EntitiesCheckpoint, ExecInput, ExecOutput, Stage, StageCheckpoint, StageError, StageId,
    StorageHashingCheckpoint, UnwindInput, UnwindOutput,
};
use reth_storage_api::StorageSettingsCache;
use reth_storage_errors::provider::ProviderResult;
use std::{
```
After
```rust
use reth_provider::{DBProvider, HashingWriter, StatsReader, StorageReader};
use reth_stages_api::{
    BlockRangeOutput, EntitiesCheckpoint, ExecInput, ExecOutput, Stage, StageCheckpoint,
    StageError, StageId, StorageHashingCheckpoint, UnwindInput, UnwindOutput,
};
use reth_storage_api::StorageSettingsCache;
use reth_storage_errors::provider::ProviderResult;
use std::{
```

# Fix Pattern

Use total outstanding work, rather than the next scheduler window, when a threshold is meant to bound memory or work across an entire catch-up operation.

## How It Was Fixed

Both hashing stages now compute the total remaining range from the target block and current checkpoint, then use that value in the clean-threshold branch. This makes the clean/full-rehash fallback depend on the full backlog instead of the size of the next batch, while preserving the existing genesis special case (`from_block == 1`).

# Why It Matters

1. It makes the memory-bounding heuristic match the full backlog rather than a potentially misleading small batch window.

2. It applies the same safeguard to both account hashing and storage hashing, which suggests a shared stage-design issue rather than a one-off bug.

3. The evidence supports an availability or robustness improvement, not a proven confidentiality, integrity, or authorization issue.

# Evidence Notes

The strongest evidence is the paired logic change in `crates/stages/stages/src/stages/hashing_storage.rs` and `crates/stages/stages/src/stages/hashing_account.rs`, where the condition changes from `to_block - from_block > self.clean_threshold` to `total_range > self.clean_threshold`, with comments explicitly stating that total remaining range is now used to decide clean versus incremental behavior. The commit subject, `fix(stages): bound storage hashing stages memory`, supports a memory-bounding interpretation. The added imports such as `BlockRangeOutput` are supporting context, not independent proof of a vulnerability. The supplied material does not show a crash, an attacker-controlled trigger, default reachability, or a semantic mismatch between clean and incremental hashing outputs. Protocol security invariant: Account and storage hashing stages should preserve the intended hashed-state result while selecting a mode that keeps memory use bounded across the full remaining catch-up range, not just the next scheduled batch. Verification notes: The patch does not prove remote exploitability or attacker control over the problematic range selection. The patch does not show state corruption or consensus divergence; clean and incremental paths appear intended to be semantically equivalent. The patch evidence supports memory-bounding/availability hardening, not a confidentiality or authorization issue. It is not proven from this diff alone whether the bug was reachable in default configurations or only during large catch-up/sync workloads. The provided evidence supports memory-bounding hardening in hashing-stage scheduling logic. The provided evidence does not prove a concrete vulnerability or exploitable denial-of-service condition. The provided evidence does not establish state corruption, consensus divergence, or other stronger security impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `availability`
Final tags: `infrastructure, storage, resource-exhaustion, availability, memory-bounding`

The patch clearly tightens memory-bounding behavior in the account and storage hashing stages by changing the clean-versus-incremental decision from the next batch window to the full remaining range. In a validator/sync pipeline, that is an availability-sensitive hardening change, and the commit subject explicitly frames it as bounding memory. However, the supplied evidence does not prove a concrete exploitable vulnerability, attacker control, default reachability, or a demonstrated remote DoS, so this should be retained only as security hardening rather than a confirmed security fix.

## Security Evidence

1. The commit subject explicitly says the change is to "bound storage hashing stages memory."
2. Both hashing stages replace a threshold check on `to_block - from_block` with a check on `total_range`, tightening the heuristic around total outstanding work.
3. The new inline comment says the code now uses the total remaining range to decide clean vs incremental behavior.
4. The affected code is in hashing stages that operate on chain state during execution/sync, where uncontrolled memory growth is security-relevant for availability.

## Missing Evidence

1. No evidence shows that an external attacker or peer can directly force this condition in a default deployment.
2. No crash, OOM, advisory, test, or bug report is provided to prove a concrete denial-of-service vulnerability.
3. No evidence shows consensus divergence, state corruption, or any integrity impact.
4. No evidence establishes that the previous behavior was reachable beyond large catch-up or sync workloads.

## Claim Boundaries

1. This patch supports a memory/availability hardening interpretation, not a proven exploitable vulnerability fix.
2. The evidence does not justify the stronger original `remote-dos` impact claim.
3. The patch does not support claims about confidentiality, authorization, or data integrity issues.
4. The patch does not by itself prove consensus breakage or semantic differences between clean and incremental hashing results.
