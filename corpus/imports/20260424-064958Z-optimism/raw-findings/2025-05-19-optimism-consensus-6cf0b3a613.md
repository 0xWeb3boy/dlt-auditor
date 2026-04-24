---
case_id: case_20250519_6cf0b3a613
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2025-05-19
source_refs:
  - git:6cf0b3a613f39a950addc9310463deb1c92d4859
  - "kona/crates/node/engine/src/task_queue/tasks/insert/task.rs:119"
  - "kona/crates/node/service/src/actors/engine.rs:109"
  - "kona/crates/node/sources/src/sync/mod.rs:38"
  - "kona/crates/node/service/src/actors/engine.rs:239"
bug_class: unsafe-forkchoice-promotion
impact_type:
  - incorrect-forkchoice-classification
confidence: medium
tags:
  - blockchain-core
  - consensus
  - forkchoice
  - startup-sync
  - state-initialization
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch hardens startup forkchoice handling in a consensus-sensitive path. The visible pre-patch code had explicit branches that could set `safe` and `finalized` to the newly inserted payload or to the current `unsafe` head during recovery. The new flow removes those shortcut promotions and instead performs a post-EL-sync reset/start routine with backward traversal from the `unsafe` head to choose a safer starting point.

## Observed Patch Facts

1. In `kona/crates/node/engine/src/task_queue/tasks/insert/task.rs`, the patch replaces `match state.sync_status {` with `if !state.sync_status.has_started() {`.

2. In `kona/crates/node/service/src/actors/engine.rs`, the patch replaces `pub fn check_sync(&self) {` with `async fn check_sync(&mut self) -> Result<(), EngineError> {`.

3. In `kona/crates/node/sources/src/sync/mod.rs`, the patch replaces `// Check if we can recover from a finality-less sync state` with `// Search for the highest 'unsafe' block, relative to the initial 'unsafe' block's L1...`.

4. In `kona/crates/node/service/src/actors/engine.rs`, the patch replaces `// Update the l2 safe head if needed.` with `Err(EngineTaskError::Reset(e)) => {`.

## Project Context

The changed code sits primarily in `kona/crates/node/engine/src/task_queue/tasks/insert`, `kona/crates/node/engine/src/task_queue/tasks`, `kona/crates/node/service/src/actors`, which anchors the finding in the `consensus` area of the project. Historical context from `kona/crates/node/service/src/actors/derivation.rs`, `kona/crates/node/service/src/actors/l1_watcher_rpc.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `kona/crates/node/service/src/actors/derivation.rs`, `kona/crates/node/engine/src/task_queue/tasks/forkchoice/task.rs`. The strongest project-level identifiers around this patch are `engine`, `state`, `head`, and `target`.

## Before/After Behavior

Before, startup-related paths could directly assign `safe` and `finalized` to the new payload hash or return a forkchoice with `safe = finalized = unsafe`. After, those branches are removed, sync completion moves into an async reset path, and startup forkchoice discovery walks backward from the current `unsafe` head using L1-origin context instead of collapsing labels onto `unsafe`.

# Root Cause

Startup logic treated sync progress as sufficient reason to promote forkchoice labels, allowing `safe` and `finalized` to be derived from the latest `unsafe` state rather than from older chain context.

## Walkthrough

1. `kona/crates/node/engine/src/task_queue/tasks/insert/task.rs` previously had an `ExecutionLayerNotFinalized` branch that set `fcu.safe_block_hash` and `fcu.finalized_block_hash` to the new payload hash.

2. That insertion path now only marks sync as started, removing the visible code that promoted the inserted payload to both safe and finalized.

3. `kona/crates/node/sources/src/sync/mod.rs` previously had a recovery branch that returned `un_safe`, `safe`, and `finalized` all equal to `current_fc.un_safe`.

4. The sync-start logic is changed to a backward search from the current `unsafe` head, querying L1-origin blocks while deriving the starting forkchoice.

5. `kona/crates/node/service/src/actors/engine.rs` changes `check_sync` into an async method and adds `self.reset().await?`, showing startup handling now runs through a reset path after EL sync.

6. A separate safe-head update block on task drain is removed, consistent with consolidating startup head selection into the reset/sync-start flow.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| kona/crates/node/sources/src/sync/mod.rs | 26 | startup forkchoice discovery now walks back from the unsafe head to derive a protocol-consistent safe head instead of recovering by equating safe/finalized with unsafe |
| kona/crates/node/engine/src/task_queue/tasks/insert/task.rs | 119 | removes the `ExecutionLayerNotFinalized` path that previously rewrote forkchoice to treat a newly inserted payload as both safe and finalized during initial sync |
| kona/crates/node/service/src/actors/engine.rs | 109 | moves sync-complete handling into an async path that can reset the engine after EL sync and then apply the safer startup routine |
| kona/crates/node/service/src/actors/engine.rs | 239 | stops using task-drain completion as the place to push ad hoc safe-head updates, consistent with centralizing safe-head selection in the reset/startup path |

## Code Snippets

## Snippet 1

Context: `kona/crates/node/engine/src/task_queue/tasks/insert/task.rs:119` (changes signature or replay validation logic)

Before
```rust
};

        match state.sync_status {
            SyncStatus::ExecutionLayerFinished => { /* Nothing to do; Continue */ }
            SyncStatus::ExecutionLayerNotFinalized => {
                // Use the new payload as the safe and finalized block for the FCU.
                fcu.safe_block_hash = self.envelope.payload.block_hash();
                fcu.finalized_block_hash = self.envelope.payload.block_hash();
```
After
```rust
};

        if !state.sync_status.has_started() {
            state.sync_status = SyncStatus::ExecutionLayerStarted;
        }
```

## Snippet 2

Context: `kona/crates/node/service/src/actors/engine.rs:109` (changes persisted or aggregate state handling)

Before
```rust
/// Checks if the engine is syncing, notifying the derivation actor if necessary.
    pub fn check_sync(&self) {
        // If the channel is closed, the receiver already marked engine ready.
        if self.sync_complete_tx.is_closed() {
            return;
        }
```
After
```rust
/// Checks if the engine is syncing, notifying the derivation actor if necessary.
    async fn check_sync(&mut self) -> Result<(), EngineError> {
        // If the channel is closed, the receiver already marked engine ready.
        if self.sync_complete_tx.is_closed() {
            return Ok(());
        }
```

## Snippet 3

Context: `kona/crates/node/sources/src/sync/mod.rs:38` (changes signature or replay validation logic)

Before
```rust
);

    // Check if we can recover from a finality-less sync state
    if should_recover_from_finality_less_sync(&current_fc, cfg) {
        warn!(
            target: "sync_start",
            "Attempting recovery from sync state without finality. Heads set to {:?}",
            current_fc.un_safe
```
After
```rust
);

    // Search for the highest `unsafe` block, relative to the initial `unsafe` block's L1 origin,
    loop {
        let l1_origin = l1_provider.get_block(current_fc.un_safe.l1_origin.hash.into()).await?;
        info!(
            target: "sync_start",
            l1_origin = %current_fc.un_safe.l1_origin.number,
```

## Snippet 4

Context: `kona/crates/node/service/src/actors/engine.rs:239` (changes persisted or aggregate state handling)

Before
```rust
match res {
                        Ok(_) => {
                          trace!(target: "engine", "[ENGINE] tasks drained");
                          // Update the l2 safe head if needed.
                          let state_safe_head = self.engine.state().safe_head();
                          let update = |head: &mut L2BlockInfo| {
                              if head != &state_safe_head {
                                  *head = state_safe_head;
```
After
```rust
match res {
                        Ok(_) => {
                            trace!(target: "engine", "[ENGINE] tasks drained");
                        }
                        Err(EngineTaskError::Reset(e)) => {
```

# Fix Pattern

Remove shortcut state promotion in startup recovery and recompute forkchoice from chain context after sync completion.

## How It Was Fixed

The fix deletes the visible branches that equated `safe`/`finalized` with a fresh payload or with `unsafe`, moves sync-complete handling into an async reset path, and changes startup forkchoice selection to walk backward from the `unsafe` head using L1-origin information.

# Why It Matters

1. `safe` and `finalized` are protocol-significant labels, not just local sync markers.

2. Blind promotion from `unsafe` weakens the distinction between tentative and protocol-backed head states.

3. Centralizing startup forkchoice derivation reduces inconsistent initialization paths.

# Evidence Notes

Directly supported by the shown removal of `safe/finalized = new payload` in `insert/task.rs`, removal of `safe = finalized = unsafe` recovery in `sources/src/sync/mod.rs`, and addition of async reset-driven sync completion in `service/src/actors/engine.rs`. The commit message explicitly frames this as a security improvement, but the provided evidence does not prove a real-world exploit or observed chain divergence. Protocol security invariant: When EL sync completes, startup forkchoice should derive `safe` and `finalized` from protocol-backed chain context, not blindly relabel the current `unsafe` head or first inserted payload as safe/finalized. Verification notes: The patch does not by itself prove remote exploitability or a practical attack path. The evidence does not show that consensus divergence definitely occurred in production. The exact finalized-head derivation rules after the change are not fully visible in the provided hunks. This is not evidence of memory corruption, key compromise, or cryptographic breakage. Evidence supports security hardening more strongly than a confirmed vulnerability. The exact post-patch finalized-head derivation is not fully visible in the provided snippets. No exploit scenario or production impact is established by the provided material. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unsafe-forkchoice-promotion`
Final impact type: `incorrect-forkchoice-classification`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, forkchoice, startup-sync, state-initialization`

The patch directly removes startup paths that could relabel a newly inserted payload or the current `unsafe` head as `safe` and `finalized`, and replaces them with a reset-driven startup routine plus backward traversal from the unsafe head using L1-origin context. That is a clear tightening of security-sensitive forkchoice behavior in a consensus path. However, the provided evidence does not prove a concrete exploitable vulnerability, real consensus break, or production incident, so this is best retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. Pre-patch code explicitly set `safe` and `finalized` to the new payload during `ExecutionLayerNotFinalized`.
2. Pre-patch recovery path could return `safe = finalized = unsafe` in `find_starting_forkchoice`.
3. Post-patch startup logic searches backward from `unsafe` using L1-origin context instead of blindly promoting heads.
4. Engine sync completion now goes through `reset().await?`, centralizing and tightening startup forkchoice initialization.
5. Commit message explicitly says the change improves security by avoiding blind promotion of `safe` and `finalized`.

## Missing Evidence

1. No proof that an attacker could trigger the bad startup state remotely.
2. No evidence of observed consensus divergence, chain split, or fund-impacting behavior.
3. No full post-patch logic showing exactly how `finalized` is derived end to end.
4. No test or advisory evidence demonstrating exploitability or prior incorrect acceptance of malicious state.

## Claim Boundaries

1. Supported claim: the patch hardens consensus-sensitive startup forkchoice handling.
2. Supported claim: previous code had shortcut promotions from `unsafe` or fresh payloads into `safe`/`finalized`.
3. Not supported: a concrete exploitable vulnerability was definitely fixed.
4. Not supported: the bug caused real-world consensus failure or validator compromise.
5. Not supported: this involved cryptographic breakage, memory corruption, or key compromise.
