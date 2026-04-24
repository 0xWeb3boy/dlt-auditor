---
case_id: case_20260304_23f3ffea2a
project: optimism
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: consensus
bug_class: consensus-safety
confidence: low
source_quality: medium
date: 2026-03-04
source_refs:
  - git:23f3ffea2aacdcebd2a68f3ad63133e276612bb9
  - "rust/kona/crates/node/engine/src/task_queue/tasks/synchronize/task.rs:66"
impact_type:
  - state-divergence
tags:
  - blockchain-core
  - consensus
  - forkchoice
  - state-divergence
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes `SynchronizeTask` so a `SYNCING` response is no longer accepted unconditionally. If the execution layer had previously finished syncing, the code now treats a new `SYNCING` response as `InvalidForkchoiceState` and triggers recovery instead of continuing with a potentially stale internal view. The supplied evidence supports a state-consistency fix, but it does not establish an attacker-driven vulnerability or concrete security impact beyond desynchronization risk.

## Observed Patch Facts

1. In `rust/kona/crates/node/engine/src/task_queue/tasks/synchronize/task.rs`, the patch replaces `// If we're not building a new payload, we're driving EL sync.` with `if state.el_sync_finished {`.

## Project Context

The changed code sits primarily in `rust/kona/crates/node/engine/src/task_queue/tasks/synchronize`, `rust/kona/crates/node/engine/src/task_queue/tasks`, which anchors the finding in the `consensus` area of the project. Historical context from `rust/kona/crates/node/engine/src/task_queue/tasks/synchronize/error.rs`, `rust/kona/crates/node/engine/src/task_queue/tasks/synchronize/mod.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rust/kona/crates/node/engine/src/task_queue/tasks/insert/task.rs`, `rust/kona/crates/node/engine/src/task_queue/tasks/build/task.rs`. The strongest project-level identifiers around this patch are `state`, `PayloadStatusEnum::Syncing`, `sync`, and `target`.

## Before/After Behavior

Before the patch, the `PayloadStatusEnum::Syncing` branch returned `Ok(())` for all cases, even after `PayloadStatusEnum::Valid` had already marked `state.el_sync_finished = true`. After the patch, `SYNCING` is still accepted during initial sync, but once `el_sync_finished` is true it produces `Err(SynchronizeTaskError::InvalidForkchoiceState)` instead.

# Root Cause

The status-handling logic did not distinguish expected `SYNCING` during initial execution-layer sync from unexpected `SYNCING` after sync had already completed, so a post-sync loss of EL state could be treated as success rather than as desynchronization.

## Walkthrough

1. `check_forkchoice_updated_status` already tracked whether execution-layer sync had completed by setting `state.el_sync_finished = true` on `PayloadStatusEnum::Valid`.

2. Before the fix, the `PayloadStatusEnum::Syncing` arm ignored that flag and always returned success.

3. The new code adds a check on `state.el_sync_finished` inside the `Syncing` arm.

4. If sync is still in progress, `SYNCING` remains accepted.

5. If sync had previously completed, the code now logs a warning and returns `InvalidForkchoiceState` instead of `Ok(())`.

6. The commit message says this error path triggers reset and forkchoice re-discovery of the EL state.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rust/kona/crates/node/engine/src/task_queue/tasks/synchronize/task.rs | 50 | forkchoice update status gate that tracks whether EL sync has completed and decides whether a returned status preserves the CL/EL state-alignment invariant |
| rust/kona/crates/node/engine/src/task_queue/tasks/synchronize/task.rs | 66 | post-sync `SYNCING` handling changed from unconditional success to reset-triggering error (`InvalidForkchoiceState`) to force forkchoice re-discovery |
| rust/kona/crates/node/engine/src/task_queue/tasks/insert/task.rs | 1 | unsafe payload insertion path that relies on the engine task queue maintaining a correct synchronized forkchoice view |
| rust/kona/crates/node/engine/src/task_queue/tasks/build/task.rs | 1 | block build/import path whose correctness depends on the same engine-state and forkchoice synchronization assumptions |

## Code Snippets

## Snippet 1

Context: `rust/kona/crates/node/engine/src/task_queue/tasks/synchronize/task.rs:66` (changes a consensus- or validator-sensitive branch)

Before
```rust
}
            PayloadStatusEnum::Syncing => {
                // If we're not building a new payload, we're driving EL sync.
                debug!(target: "engine", "Attempting to update forkchoice state while EL syncing");
                Ok(())
            }
            s => {
```
After
```rust
}
            PayloadStatusEnum::Syncing => {
                if state.el_sync_finished {
                    // EL was previously synced but is now returning SYNCING,
                    // indicating state divergence (e.g. after EL restart where
                    // in-memory state was lost). Trigger a reset to re-discover
                    // the EL's actual chain state.
                    warn!(target: "engine", "EL returned SYNCING after sync was previously completed, triggering reset");
```

# Fix Pattern

Make status handling stateful at the forkchoice boundary: allow a transient status during bootstrap, but treat the same status as an error after the subsystem has transitioned into steady state.

## How It Was Fixed

The fix gates acceptance of `PayloadStatusEnum::Syncing` on `state.el_sync_finished`. Post-sync `SYNCING` is converted into `InvalidForkchoiceState`, causing recovery rather than silent continuation.

# Why It Matters

1. Prevents silent acceptance of a status that can indicate CL/EL state mismatch after sync completed.

2. Turns a stale-state condition into explicit recovery behavior.

3. Preserves expected behavior for normal initial synchronization.

# Evidence Notes

Direct code evidence is limited to `rust/kona/crates/node/engine/src/task_queue/tasks/synchronize/task.rs`, where the `Syncing` branch changed from unconditional success to conditional erroring based on `state.el_sync_finished`. The nearby `Valid` branch shows that flag being set. The stronger claims about EL restart, loss of in-memory state, reset severity, and `find_starting_forkchoice` come from the commit message, not from the shown diff. Related task-queue files only show surrounding subsystem context, not additional proof of exploitability or concrete security impact. Protocol security invariant: After the execution layer has been observed as synced, a later `SYNCING` response to forkchoice updates must be treated as loss of state alignment rather than as normal progress; the node should re-discover the execution layer's actual chain state before continuing. Verification notes: The patch does not prove a remote attacker can force the EL restart or state loss condition. It does not prove a finalized-chain safety failure or permanent chain split occurred on-chain. It does not show authentication, authorization, memory-safety, or cryptographic verification issues. It does not establish impact beyond CL/EL state divergence, reset behavior, and potential protocol instability. No test diff or runtime reproduction was provided. Recovery-path effects beyond returning `InvalidForkchoiceState` are inferred from the commit message. The evidence supports a correctness and state-alignment fix more clearly than a confirmed security vulnerability. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `state-divergence`
Final tags: `blockchain-core, consensus, forkchoice, state-divergence`

The patch is in a consensus-sensitive engine path and changes post-sync `SYNCING` from unconditional success to an error that forces state re-discovery. That clearly hardens handling of a risky stale-state condition between the consensus-layer view and execution-layer reality. However, the supplied evidence does not prove an attacker-triggerable vulnerability or a demonstrated consensus break, so this is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. The changed branch is in forkchoice status handling for the engine synchronization task.
2. Before the patch, `PayloadStatusEnum::Syncing` always returned success even after `el_sync_finished` was true.
3. After the patch, post-sync `SYNCING` becomes `InvalidForkchoiceState`, which forces recovery instead of silent continuation.
4. The commit message explicitly describes CL/EL state divergence and reset-based recovery in a consensus-sensitive subsystem.

## Missing Evidence

1. No proof that an external attacker can cause the EL restart or state-loss condition.
2. No evidence of a concrete exploit, chain split, finalized-state corruption, or fund-impact outcome.
3. No test or runtime evidence showing security impact beyond stale-state divergence risk.

## Claim Boundaries

1. Supported claim: the patch hardens consensus-state synchronization and recovery behavior.
2. Supported claim: it reduces risk of silently operating with a stale forkchoice view after EL state loss.
3. Unsupported claim: this patch alone proves a remotely exploitable consensus vulnerability.
4. Unsupported claim: this evidence alone proves an actual consensus failure occurred in production.
