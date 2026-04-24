---
case_id: case_20250519_dfafb52630
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2025-05-19
source_refs:
  - git:dfafb52630dbb3d86977b232eea79b135d8ad048
  - "crates/node/engine/src/task_queue/tasks/insert/task.rs:119"
  - "crates/node/service/src/actors/engine.rs:109"
  - "crates/node/sources/src/sync/mod.rs:38"
  - "crates/node/service/src/actors/engine.rs:239"
bug_class: improper-forkchoice-initialization
impact_type:
  - incorrect-forkchoice-state
tags:
  - blockchain-core
  - consensus
  - forkchoice
  - startup-sync
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch removes startup and recovery paths that directly copied the current unsafe payload or unsafe head into the safe/finalized forkchoice fields, and replaces them with a post-EL-sync startup routine that derives a safe starting point by traversing backward from the unsafe head. The evidence supports a consensus-sensitive security hardening in forkchoice initialization, but not a fully demonstrated exploit.

## Observed Patch Facts

1. In `crates/node/engine/src/task_queue/tasks/insert/task.rs`, the patch replaces `match state.sync_status {` with `if !state.sync_status.has_started() {`.

2. In `crates/node/service/src/actors/engine.rs`, the patch replaces `pub fn check_sync(&self) {` with `async fn check_sync(&mut self) -> Result<(), EngineError> {`.

3. In `crates/node/sources/src/sync/mod.rs`, the patch replaces `// Check if we can recover from a finality-less sync state` with `// Search for the highest 'unsafe' block, relative to the initial 'unsafe' block's L1...`.

4. In `crates/node/service/src/actors/engine.rs`, the patch replaces `// Update the l2 safe head if needed.` with `Err(EngineTaskError::Reset(e)) => {`.

## Project Context

The changed code sits primarily in `crates/node/engine/src/task_queue/tasks/insert`, `crates/node/engine/src/task_queue/tasks`, `crates/node/service/src/actors`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/node/service/src/actors/derivation.rs`, `crates/node/service/src/actors/l1_watcher_rpc.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/node/service/src/actors/derivation.rs`, `crates/node/engine/src/task_queue/tasks/forkchoice/task.rs`. The strongest project-level identifiers around this patch are `engine`, `state`, `head`, and `target`.

## Before/After Behavior

Before the patch, one startup path in insert handling set `safe_block_hash` and `finalized_block_hash` to the newly inserted payload when `SyncStatus::ExecutionLayerNotFinalized` was hit, and one recovery path returned forkchoice with `safe` and `finalized` both equal to `current_fc.un_safe`. After the patch, the insert path only marks sync as started, the direct recovery shortcut is removed, and startup forkchoice selection is deferred to logic that searches backward from the unsafe head using L1-origin history.

# Root Cause

A startup shortcut treated the current unsafe block as safe/finalized based on sync state rather than deriving those labels from the rollup's chain-context rule.

## Walkthrough

1. In `crates/node/engine/src/task_queue/tasks/insert/task.rs`, the removed `SyncStatus::ExecutionLayerNotFinalized` branch explicitly assigned both `fcu.safe_block_hash` and `fcu.finalized_block_hash` to the new payload hash.

2. That shows the old startup path could promote the just-inserted unsafe payload into stronger forkchoice labels during EL sync transition.

3. In `crates/node/sources/src/sync/mod.rs`, the removed `should_recover_from_finality_less_sync` path returned a forkchoice where `safe` and `finalized` were both `current_fc.un_safe`.

4. The new `sync/mod.rs` code instead starts a backward search from the current unsafe head and loads each candidate's L1 origin.

5. The commit message states the intended criterion: choose a safe block whose L1 origin is at least one sequence window behind the unsafe head's L1 origin.

6. In `crates/node/service/src/actors/engine.rs`, `check_sync` becomes async and the shown path performs `reset().await?` before startup continues, supporting that initialization was moved out of the inline insertion shortcut.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/node/engine/src/task_queue/tasks/insert/task.rs | 119 | removes the startup shortcut that set safe_block_hash and finalized_block_hash to the newly inserted unsafe payload when EL sync first finished |
| crates/node/sources/src/sync/mod.rs | 26 | replaces finality-less recovery with backward traversal from the unsafe head to derive a startup safe forkchoice candidate from L1-origin distance |
| crates/node/service/src/actors/engine.rs | 109 | moves sync-complete handling to an async reset/start-derivation path so forkchoice initialization happens after EL sync rather than during initial insertion |

## Code Snippets

## Snippet 1

Context: `crates/node/engine/src/task_queue/tasks/insert/task.rs:119` (changes signature or replay validation logic)

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

Context: `crates/node/service/src/actors/engine.rs:109` (changes persisted or aggregate state handling)

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

Context: `crates/node/sources/src/sync/mod.rs:38` (changes signature or replay validation logic)

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

Context: `crates/node/service/src/actors/engine.rs:239` (changes persisted or aggregate state handling)

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

Remove blind promotion of sensitive forkchoice state at a startup transition and recompute the startup safe point from protocol-specific chain history before resuming normal processing.

## How It Was Fixed

The patch removes the insert-time branch that forced `safe` and `finalized` to the current payload, removes the recovery shortcut that collapsed all heads to `un_safe`, and introduces a startup forkchoice search that walks backward from the unsafe head using L1-origin distance. Sync-complete handling is also moved into an explicit async reset/startup path instead of piggybacking on initial unsafe insertion.

# Why It Matters

1. It stops startup code from treating the current unsafe block as safe/finalized just because sync advanced.

2. It narrows forkchoice labeling to a chain-history-derived rule instead of a status-driven shortcut.

3. It affects a consensus-sensitive path even though the provided evidence does not prove broader network impact.

# Evidence Notes

The strongest evidence is direct: old code in `insert/task.rs` set `safe_block_hash` and `finalized_block_hash` to the current payload hash, and old code in `sync/mod.rs` returned `safe` and `finalized` equal to `current_fc.un_safe`. The new `sync/mod.rs` excerpt shows a backward search over L1 origins, and the commit message explains the sequence-window criterion. The `engine.rs` excerpt supports that startup handling moved to an async reset path. No test evidence or incident evidence was provided, so the security claim should stay at hardening/likely rather than confirmed exploit. Protocol security invariant: During sync startup, the node should not mark an L2 block as "safe" or "finalized" solely because EL sync reached a transition point; those labels should be derived from chain context. The provided evidence supports that the new path derives startup forkchoice by walking backward from the unsafe head and using L1-origin distance instead of blindly promoting the current unsafe block. Verification notes: The patch proves incorrect startup forkchoice labeling, not arbitrary payload acceptance. It does not prove a remotely triggerable exploit path from untrusted peers alone. It does not prove a persistent chain split or finalized-state corruption beyond startup-state selection. It does not show concrete asset loss, privilege escalation, or cryptographic breakage. The provided excerpts support removal of blind startup promotion, but not full end-to-end proof of exploitability. The exact safety condition is partly described by the commit message rather than fully visible in the code excerpts. No tests or reproducer were supplied in the provided input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `improper-forkchoice-initialization`
Final impact type: `incorrect-forkchoice-state`
Final tags: `blockchain-core, consensus, forkchoice, startup-sync`

The supplied patch evidence supports a consensus-sensitive hardening: it removes startup and recovery paths that directly promoted the current unsafe payload or unsafe head into `safe` and `finalized` forkchoice state, and replaces that with a more conservative sync-start routine based on chain history. That is security-relevant in a blockchain node, and the commit message explicitly frames it as a security improvement. However, the excerpts do not prove a concrete exploitable vulnerability, attacker trigger, or demonstrated consensus failure, so this is best retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. Old insert-time logic explicitly set `safe_block_hash` and `finalized_block_hash` to the current payload hash during an EL sync transition.
2. Old sync-start recovery logic could return forkchoice with `safe` and `finalized` both equal to `current_fc.un_safe`.
3. New sync-start logic replaces that shortcut with backward traversal from the unsafe head using L1-origin history.
4. Sync-complete handling was moved into an explicit reset/startup path instead of piggybacking on unsafe payload insertion.
5. The commit message explicitly says the change improves security by avoiding blind promotion of `safe` and `finalized`.

## Missing Evidence

1. No reproducer, test, or incident demonstrates that the old behavior was exploitable.
2. The provided excerpts do not show full end-to-end enforcement of the new safety criterion.
3. No evidence shows an actual chain split, finalized-state corruption, or attacker-controlled impact.

## Claim Boundaries

1. The patch supports that prior startup forkchoice labeling was overly permissive for `safe` and `finalized` state.
2. The patch does not by itself prove a concrete exploitable bug or real-world compromise.
3. The strongest defensible corpus label is security hardening of forkchoice initialization, not a confirmed consensus-break fix.
