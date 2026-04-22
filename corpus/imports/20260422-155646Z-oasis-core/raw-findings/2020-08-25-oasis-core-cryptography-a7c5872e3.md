---
case_id: case_20200825_a7c5872e3
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2020-08-25
source_refs:
  - git:a7c5872e3be394e932c71d27cf6d54fc1f300083
  - "go/consensus/tendermint/apps/roothash/roothash.go:241"
  - "go/consensus/tendermint/apps/roothash/roothash.go:584"
  - "go/consensus/tendermint/apps/roothash/roothash.go:156"
  - "go/consensus/tendermint/apps/roothash/roothash.go:492"
bug_class: stale-timeout-state
impact_type:
  - state-consistency
  - liveness-disruption
confidence: medium
tags:
  - consensus
  - timeout-lifecycle
  - state-management
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied diff supports a real timeout-lifecycle bug in roothash round handling, not a proven vulnerability. Before the patch, `emitEmptyBlock` reset executor commitments without clearing a previously scheduled round timeout. After the patch, it clears `NextTimeout` from persistent state and propagates errors to callers. That shows stale timeout cleanup was missing on some round-transition paths, but the evidence here does not establish attacker-controlled exploitation or a confirmed security failure.

## Observed Patch Facts

1. In `go/consensus/tendermint/apps/roothash/roothash.go`, the patch replaces `runtime.ExecutorPool.ResetCommitments()` with `// Clear timeout if there was one scheduled.`.

2. In `go/consensus/tendermint/apps/roothash/roothash.go`, the patch replaces `finalizedBlock := app.tryFinalizeExecutor(ctx, rtState, forced)` with `finalizedBlock, err := app.tryFinalizeExecutorCommits(ctx, rtState, forced)`.

3. In `go/consensus/tendermint/apps/roothash/roothash.go`, the patch replaces `app.emitEmptyBlock(ctx, rtState, block.EpochTransition)` with `if err = app.emitEmptyBlock(ctx, rtState, block.EpochTransition); err != nil {`.

4. In `go/consensus/tendermint/apps/roothash/roothash.go`, the patch replaces `app.emitEmptyBlock(ctx, rtState, block.RoundFailed)` with `if err := app.emitEmptyBlock(ctx, rtState, block.RoundFailed); err != nil {`.

## Project Context

The changed code sits primarily in `go/consensus/tendermint/apps/roothash`, `go/consensus/tendermint/apps`, which anchors the finding in the `cryptography` area of the project. Historical context from `go/consensus/tendermint/apps/roothash/transactions.go`, `go/consensus/tendermint/apps/roothash/genesis.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/consensus/tendermint/apps/roothash/transactions.go`, `go/consensus/tendermint/apps/roothash/genesis.go`. The strongest project-level identifiers around this patch are `rtState`, `block`, `runtime`, and `ExecutorPool`.

## Before/After Behavior

Before the patch, `emitEmptyBlock` updated block state and called `runtime.ExecutorPool.ResetCommitments()` without clearing a persisted round timeout in the shown path. After the patch, if `runtime.ExecutorPool.NextTimeout` is set, it calls `state.ClearRoundTimeout(...)` before resetting commitments and returns an error if cleanup fails. Callers in the epoch-transition and round-failure paths were also changed to stop on `emitEmptyBlock` errors instead of ignoring them.

# Root Cause

A round-transition helper (`emitEmptyBlock`) did not perform the same timeout-state cleanup that the finalization path already treated as part of normal round lifecycle management. As a result, a previously armed timeout could remain in persistent state when commitments were reset via the empty-block path.

## Walkthrough

1. The existing `tryFinalizeBlock` context already models timeout clear/re-arm as explicit state management.

2. The pre-patch `emitEmptyBlock` snippet shows block updates followed by `ResetCommitments()` but no timeout clear in that path.

3. `emitEmptyBlock` is used in important round-transition cases, including epoch transition and round-failed handling.

4. The patch adds a check for `NextTimeout != commitment.TimeoutNever` and clears that timeout from mutable roothash state before resetting commitments.

5. The patch also changes callers to propagate `emitEmptyBlock` errors, so failed timeout cleanup is no longer silently ignored.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/apps/roothash/roothash.go | 237 | core fix in `emitEmptyBlock`; clears persisted round timeout before resetting executor commitments |
| go/consensus/tendermint/apps/roothash/roothash.go | 545 | round-finalization path that already clears/re-arms timeouts; establishes expected timeout lifecycle across finalize transitions |
| go/consensus/tendermint/apps/roothash/roothash.go | 150 | epoch-transition caller now handling `emitEmptyBlock` failure instead of ignoring timeout-cleanup errors |
| go/consensus/tendermint/apps/roothash/roothash.go | 486 | round-failure path now handling `emitEmptyBlock` failure instead of silently proceeding after failed cleanup |

## Code Snippets

## Snippet 1

Context: `go/consensus/tendermint/apps/roothash/roothash.go:241` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
runtime.CurrentBlockHeight = ctx.BlockHeight()
	if runtime.ExecutorPool != nil {
		runtime.ExecutorPool.ResetCommitments()
	}
```
After
```go
runtime.CurrentBlockHeight = ctx.BlockHeight()
	if runtime.ExecutorPool != nil {
		// Clear timeout if there was one scheduled.
		if runtime.ExecutorPool.NextTimeout != commitment.TimeoutNever {
			state := roothashState.NewMutableState(ctx.State())
			if err := state.ClearRoundTimeout(ctx, runtime.Runtime.ID, runtime.ExecutorPool.NextTimeout); err != nil {
				return fmt.Errorf("failed to clear round timeout: %w", err)
			}
```

## Snippet 2

Context: `go/consensus/tendermint/apps/roothash/roothash.go:584` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}(rtState.ExecutorPool.NextTimeout)

	finalizedBlock := app.tryFinalizeExecutor(ctx, rtState, forced)
	if finalizedBlock == nil {
		return nil
	}

	app.postProcessFinalizedBlock(ctx, rtState, finalizedBlock)
```
After
```go
}(rtState.ExecutorPool.NextTimeout)

	finalizedBlock, err := app.tryFinalizeExecutorCommits(ctx, rtState, forced)
	if err != nil {
		return fmt.Errorf("failed to finalize executor commits: %w", err)
	}
	if finalizedBlock == nil {
		return nil
```

## Snippet 3

Context: `go/consensus/tendermint/apps/roothash/roothash.go:156` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
// Emit an empty epoch transition block in the new round. This is required so that
			// the clients can be sure what state is final when an epoch transition occurs.
			app.emitEmptyBlock(ctx, rtState, block.EpochTransition)

			// Set the executor pool.
```
After
```go
// Emit an empty epoch transition block in the new round. This is required so that
			// the clients can be sure what state is final when an epoch transition occurs.
			if err = app.emitEmptyBlock(ctx, rtState, block.EpochTransition); err != nil {
				return fmt.Errorf("failed to emit empty block: %w", err)
			}

			// Set the executor pool.
```

## Snippet 4

Context: `go/consensus/tendermint/apps/roothash/roothash.go:492` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
)

	app.emitEmptyBlock(ctx, rtState, block.RoundFailed)
	return nil
}

func (app *rootHashApplication) postProcessFinalizedBlock(ctx *tmapi.Context, rtState *roothashState.RuntimeState, blk *block.Block) {
	sc := ctx.StartCheckpoint()
```
After
```go
)

	if err := app.emitEmptyBlock(ctx, rtState, block.RoundFailed); err != nil {
		return nil, fmt.Errorf("failed to emit empty block: %w", err)
	}

	return nil, nil
}
```

# Fix Pattern

Align a special-case state-transition helper with the main timeout lifecycle logic, and make cleanup failures explicit instead of best-effort.

## How It Was Fixed

The fix adds explicit `ClearRoundTimeout` handling to `emitEmptyBlock` when an executor pool has a scheduled timeout, then threads returned errors through callers so transition code aborts if cleanup fails.

# Why It Matters

1. Avoids leaving obsolete timeout state behind during empty-block transitions.

2. Keeps timeout bookkeeping consistent across different round-transition paths.

3. Prevents cleanup failures from being silently ignored.

# Evidence Notes

The code directly shows missing timeout cleanup in `emitEmptyBlock` and added error propagation at its callers. It does not, by itself, show untrusted triggerability, validator divergence, consensus safety break, or another demonstrated exploit path. Protocol security invariant: Round-timeout state must stay consistent with the active executor round; when an empty block ends or transitions a round, any previously scheduled timeout for that round should be cleared before commitments are reset and the new state proceeds. Verification notes: The patch does not prove a stale timeout was reachable from untrusted input alone. The patch does not show a confirmed consensus safety failure; the visible risk is stale timeout processing and liveness/state-machine disruption. The evidence does not quantify network impact, validator divergence rate, or exploit reliability. The provided diff does not establish any cryptographic break, authorization bypass, or memory-safety issue. No test hunk was provided, so regression coverage cannot be validated from the supplied evidence. The diff supports a state-management bug and hardening-style fix, but not a confirmed security exploit. No evidence here quantifies impact on liveness, safety, or attacker control. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `stale-timeout-state`
Final impact type: `state-consistency, liveness-disruption`
Final confidence: `medium`
Final tags: `consensus, timeout-lifecycle, state-management`

The supplied patch does not prove a concrete exploitable vulnerability, but it does show a security-sensitive consensus path was leaving a previously scheduled round timeout armed across empty-block round transitions and was silently ignoring cleanup failures. Clearing the persisted timeout in `emitEmptyBlock` and propagating errors on epoch-transition and round-failure paths is a meaningful hardening change for roothash state-machine integrity. That supports keeping this as a conservative security-hardening case, not as a confirmed security bug.

## Security Evidence

1. `emitEmptyBlock` now calls `ClearRoundTimeout` before resetting executor commitments when `NextTimeout` is set.
2. The change occurs in roothash consensus round-transition logic, where stale scheduled state can affect block/round progression.
3. Callers on epoch transition and round failure now return errors instead of proceeding after failed timeout cleanup.
4. `tryFinalizeBlock` already treated timeout clear/re-arm as explicit state management, and this patch aligns the empty-block path with that invariant.

## Missing Evidence

1. No proof that an attacker or malicious committee member could reliably trigger and exploit the stale-timeout condition.
2. No demonstrated chain split, finalized-state corruption, or validator divergence caused by the pre-patch behavior.
3. No supplied regression test or reproducer showing the bug before the fix.
4. No evidence quantifying whether impact was safety-related, liveness-only, or purely internal correctness.

## Claim Boundaries

1. Supported: the pre-patch empty-block path could leave obsolete round-timeout state behind.
2. Supported: the patch hardens consensus timeout lifecycle handling and error propagation.
3. Not supported: a confirmed exploit, authorization bypass, cryptographic failure, or memory-safety issue.
4. Not supported: guaranteed client-view divergence or consensus safety failure from the provided diff alone.
