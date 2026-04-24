---
case_id: case_20250519_1681ca2942
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
bug_class: consensus-safety
confidence: medium
source_quality: high
date: 2025-05-19
source_refs:
  - git:1681ca2942eff38d2dd4fc2d8546c09040f8a171
  - "crates/node/engine/src/task_queue/tasks/insert/task.rs:119"
  - "crates/node/service/src/actors/engine.rs:109"
  - "crates/node/sources/src/sync/mod.rs:38"
  - "crates/node/service/src/actors/engine.rs:239"
impact_type:
  - incorrect-forkchoice-state
tags:
  - blockchain-core
  - consensus
  - forkchoice
  - startup-sync
  - finality
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch removes startup paths that collapsed forkchoice onto the current unsafe/newly inserted block and replaces them with a post-sync forkchoice search plus engine reset flow. The evidence supports a consensus-sensitive forkchoice hardening change, but not a proven exploit or demonstrated chain split.

## Observed Patch Facts

1. In `crates/node/engine/src/task_queue/tasks/insert/task.rs`, the patch replaces `match state.sync_status {` with `if !state.sync_status.has_started() {`.

2. In `crates/node/service/src/actors/engine.rs`, the patch replaces `pub fn check_sync(&self) {` with `async fn check_sync(&mut self) -> Result<(), EngineError> {`.

3. In `crates/node/sources/src/sync/mod.rs`, the patch replaces `// Check if we can recover from a finality-less sync state` with `// Search for the highest 'unsafe' block, relative to the initial 'unsafe' block's L1...`.

4. In `crates/node/service/src/actors/engine.rs`, the patch replaces `// Update the l2 safe head if needed.` with `Err(EngineTaskError::Reset(e)) => {`.

## Project Context

The changed code sits primarily in `crates/node/engine/src/task_queue/tasks/insert`, `crates/node/engine/src/task_queue/tasks`, `crates/node/service/src/actors`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/node/service/src/actors/derivation.rs`, `crates/node/service/src/actors/l1_watcher_rpc.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/node/service/src/actors/derivation.rs`, `crates/node/engine/src/task_queue/tasks/forkchoice/task.rs`. The strongest project-level identifiers around this patch are `engine`, `state`, `head`, and `target`.

## Before/After Behavior

Before, startup logic could set safe and finalized to the first synced payload or return a forkchoice with unsafe, safe, and finalized all equal to the unsafe head. After, startup keeps existing safe/finalized heads during payload insertion, delays sync-start forkchoice selection until after EL sync, and computes startup forkchoice by walking backward from the unsafe head before derivation proceeds.

# Root Cause

Startup forkchoice classification was driven by sync-stage shortcuts and a recovery shortcut that promoted the current unsafe/new payload to safe and finalized, instead of deriving those heads from stronger protocol context.

## Walkthrough

1. In `crates/node/engine/src/task_queue/tasks/insert/task.rs`, the removed `ExecutionLayerNotFinalized` branch explicitly assigned both `safe_block_hash` and `finalized_block_hash` to the new payload hash.

2. In `crates/node/sources/src/sync/mod.rs`, the removed recovery branch returned `{ un_safe, safe, finalized }` all equal to `current_fc.un_safe`.

3. The new insert path shown no longer performs that promotion; it keeps forkchoice hashes from the existing engine state and only marks sync as started.

4. The new sync-start path shown now performs a backward search from the current unsafe head using L1-origin data, matching the commit description that startup should derive a safer block instead of reusing the unsafe head.

5. In `crates/node/service/src/actors/engine.rs`, sync completion handling now goes through `reset().await?` and `maybe_update_safe_head()` before derivation startup, moving startup onto the recomputed forkchoice path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/node/sources/src/sync/mod.rs | 26 | computes the starting L2 forkchoice after EL sync by traversing back from the unsafe head instead of recovering by promoting unsafe to safe/finalized |
| crates/node/engine/src/task_queue/tasks/insert/task.rs | 71 | stops auto-promoting the inserted payload to safe/finalized during the initial EL sync transition and only marks sync as started |
| crates/node/service/src/actors/engine.rs | 93 | moves sync completion handling into an engine reset/startup flow that applies the safer forkchoice initialization before derivation proceeds |

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

Remove implicit head promotion at a sensitive state transition and recompute startup forkchoice from protocol-derived context before enabling downstream processing.

## How It Was Fixed

The patch deletes the special startup and recovery cases that set safe/finalized equal to the current unsafe or newly inserted payload. It instead delays startup forkchoice determination until EL sync completes, searches backward from the unsafe head using L1-origin context to choose a safer starting point, and wires sync completion through an engine reset/update sequence before derivation continues.

# Why It Matters

1. It prevents the node from overstating confirmation or finality during startup.

2. It reduces reliance on sync-progress shortcuts in consensus-sensitive state selection.

3. It makes startup forkchoice derivation depend on protocol context rather than the latest unsafe head alone.

# Evidence Notes

The patch removes a startup path that blindly copied the first synced payload into `safe` and `finalized`, and replaces it with a post-sync forkchoice search that walks backward from the unsafe head to find an older eligible safe block. The changed logic sits in the engine reset and sync-start path, so the real subsystem is startup forkchoice/state initialization rather than a generic refactor. This is security-relevant consensus/forkchoice hardening, but the provided evidence does not prove a concrete exploit beyond incorrect head promotion during startup. Protocol security invariant: During EL sync startup, the node must not mark the current unsafe L2 head as safe or finalized just because sync progressed or a recovery path was taken; startup forkchoice should be derived from an older eligible L2 block based on L1-origin context, or from genuinely finalized state. Verification notes: The patch does not prove remote code execution or a network-reachable exploit. The evidence does not show confirmed chain divergence, fund loss, or production impact. It is not proven that finalized consensus rules were violated on-chain; the issue shown is startup head classification. The available hunks do not establish which adversary capabilities, if any, are required to trigger the bad state. Security relevance is supported by the direct removal of unsafe-to-safe/finalized promotion in forkchoice startup logic. Confidence stays medium because the excerpts do not show the full selection criteria or downstream consequences. The strongest grounded classification is security hardening in a consensus-sensitive startup path, not a proven exploitable vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `incorrect-forkchoice-state`
Final tags: `blockchain-core, consensus, forkchoice, startup-sync, finality`

The patch evidence supports a security-relevant hardening change in a consensus-sensitive startup path. The removed code explicitly promoted a newly inserted or current unsafe block to `safe` and `finalized` during sync startup/recovery, and the new logic delays startup selection until after EL sync and derives a safer forkchoice by walking backward using L1-origin context. That is a real tightening of security-sensitive behavior, but the patch alone does not prove a concrete exploitable vulnerability, chain split, or production impact, so this should be retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. Removed code that set `safe_block_hash` and `finalized_block_hash` to the newly inserted payload during startup sync.
2. Removed recovery logic that returned `{ un_safe, safe, finalized }` all equal to the unsafe head.
3. New startup logic searches backward from the unsafe head using L1-origin data instead of blindly promoting the current head.
4. Sync completion now routes through engine reset/startup handling before derivation proceeds, indicating deliberate re-initialization of forkchoice state.
5. Commit message explicitly states the prior routine was less secure because it blindly promoted `safe` and `finalized` when EL sync first finished.

## Missing Evidence

1. No proof that an attacker could reliably trigger the bad startup state in a real deployment.
2. No evidence of an observed chain split, invalid finality acceptance, or fund-impacting consequence.
3. No test or trace showing downstream consensus failure from the removed promotion behavior.
4. No adversary model or network-reachability details are provided in the patch excerpts.

## Claim Boundaries

1. The evidence supports consensus/forkchoice hardening during startup sync, not a demonstrated exploitable bug.
2. The patch shows removal of risky head promotion, but does not prove on-chain consensus violation actually occurred.
3. This should not be labeled as confirmed `consensus-failure` from the supplied diff alone.
4. The security relevance is confined to startup forkchoice/state initialization behavior shown in the patch.
