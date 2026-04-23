---
case_id: case_20260212_66d78e539
project: nitro
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
impact_type:
  - state-integrity
source_quality: medium
date: 2026-02-12
source_refs:
  - git:66d78e539998cffc70883762fed0dc9e3ab01ac0
  - "arbos/block_processor.go:267"
  - "arbos/block_processor.go:516"
  - "arbos/block_processor.go:639"
  - "arbos/block_processor.go:357"
bug_class: consensus-divergence
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - consensus-divergence
  - state-integrity
  - determinism
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The evidence supports a consensus-divergence fix in `ProduceBlockAdvanced` for retryable auto-redeems. The patch adds group-level checkpointing around a user transaction and its generated redeems so that if a redeem triggers `state.ErrArbTxFilter`, the whole tentative group is reverted rather than only dropping the redeem.

## Observed Patch Facts

1. In `arbos/block_processor.go`, the patch replaces `for {` with `// Group checkpoint state for cascading redeem filtering. We take a state`.

2. In `arbos/block_processor.go`, the patch replaces `logLevel := log.Debug` with `// Cascading redeem filtering: if a redeem was filtered and we have an`.

3. In `arbos/block_processor.go`, the patch replaces `if statedb.IsTxFiltered() {` with `// Flush deferred Finalise for the last clean group`.

4. In `arbos/block_processor.go`, the patch replaces `startRefund := statedb.GetRefund()` with `// Take group checkpoint before processing user tx`.

## Project Context

Historical context from `arbos/tx_processor.go`, `arbos/vector_test.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `arbos/tx_processor.go`, `arbos/util/util.go`. The strongest project-level identifiers around this patch are `group`, `activeGroupCP`, `redeems`, and `checkpoint`.

## Before/After Behavior

Before the change, the provided evidence shows the processing loop handled user transactions and FIFO redeems without the new group checkpoint structure. The commit explains that dropping only a filtered redeem could leave replay able to regenerate and execute that redeem because replay uses a no-op redeem filter, producing a different state root. After the change, the block processor snapshots state and accounting before each user transaction, processes the user transaction and its redeems tentatively with finalization deferred, reverts the active group on `state.ErrArbTxFilter` from a redeem, and finalizes clean groups later.

# Root Cause

The root cause was non-atomic handling of a user transaction and the retryable auto-redeems generated from it in block production. Filtering only the redeem could leave sequencer-produced block state inconsistent with replay, where the redeem could be regenerated and executed under different hook behavior.

## Walkthrough

1. A user transaction processed by `ProduceBlockAdvanced` may generate retryable auto-redeems.

2. Before the patch, the supplied diff does not show a group-level checkpoint around the user transaction and its redeems.

3. A redeem can be checked through `sequencingHooks.RedeemFilter(statedb)`.

4. The commit describes the problematic case where a redeem touching a filtered address was dropped during sequencing.

5. During replay, the redeem filter may return nil, allowing the redeem to execute and produce a different state root.

6. The patch defines `groupCheckpoint` state and creates one before each user transaction.

7. While a group checkpoint is active, finalization is deferred so the snapshot remains usable across the group.

8. If a redeem fails with `state.ErrArbTxFilter`, the processor calls `revertToGroupCheckpoint()` and continues without committing that group.

9. If the group completes cleanly, deferred `statedb.Finalise(true)` is flushed.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| arbos/block_processor.go | 267 | Defines group checkpoint state used to process a user transaction and its generated redeems tentatively. |
| arbos/block_processor.go | 357 | Takes a state and accounting checkpoint before each user transaction so the whole group can be reverted. |
| arbos/block_processor.go | 471 | Runs redeem filtering through sequencing hooks while finalization may be deferred for active groups. |
| arbos/block_processor.go | 516 | On ErrArbTxFilter from a redeem, reverts the entire active user transaction group instead of only dropping the redeem. |
| arbos/block_processor.go | 639 | Flushes deferred Finalise for the last clean group after tentative processing succeeds. |

## Code Snippets

## Snippet 1

Context: `arbos/block_processor.go:267` (changes signature or replay validation logic)

Before
```go
firstTx := types.NewTx(startTx)

	for {
		// repeatedly process the next tx, doing redeems created along the way in FIFO order
```
After
```go
firstTx := types.NewTx(startTx)

	// Group checkpoint state for cascading redeem filtering. We take a state
	// checkpoint before each user tx and process it with all its redeems
	// tentatively (skipFinalise). If any redeem hits RedeemFilter, we revert
	// the entire group. If all redeems are clean, we flush Finalise.
	// lint:require-exhaustive-initialization
	type groupCheckpoint struct {
```

## Snippet 2

Context: `arbos/block_processor.go:516` (changes persisted or aggregate state handling)

Before
```go
if err != nil {
			logLevel := log.Debug
			if chainConfig.DebugMode() {
```
After
```go
if err != nil {
			// Cascading redeem filtering: if a redeem was filtered and we have an
			// active group checkpoint, revert the entire group (user tx + all redeems)
			if isRedeem && activeGroupCP != nil && errors.Is(err, state.ErrArbTxFilter) {
				if err := revertToGroupCheckpoint(); err != nil {
					return nil, nil, err
				}
```

## Snippet 3

Context: `arbos/block_processor.go:639` (changes a sensitive control or state-update path)

Before
```go
}

	if statedb.IsTxFiltered() {
		return nil, nil, state.ErrArbTxFilter
```
After
```go
}

	// Flush deferred Finalise for the last clean group
	if activeGroupCP != nil {
		statedb.Finalise(true)
		activeGroupCP = nil
	}
```

## Snippet 4

Context: `arbos/block_processor.go:357` (changes signature or replay validation logic)

Before
```go
options = conditionalOptions
			}
		}

		startRefund := statedb.GetRefund()
		if startRefund != 0 {
			return nil, nil, fmt.Errorf("at beginning of tx statedb has non-zero refund %v", startRefund)
		}
```
After
```go
options = conditionalOptions
			}

			// Take group checkpoint before processing user tx
			if isUserTx {
				activeGroupCP = &groupCheckpoint{
					snap:                 statedb.Snapshot(),
					headerGasUsed:        header.GasUsed,
```

# Fix Pattern

Enforce group-level atomicity for consensus-sensitive derived transactions: snapshot before the originating transaction, process derived work tentatively, defer irreversible finalization, and revert the whole group on a redeem-filter failure.

## How It Was Fixed

The patch records a state snapshot plus gas, balance, receipt, and completed-transaction accounting before each user transaction. It processes the user transaction and generated redeems under an active checkpoint, defers finalization while the checkpoint is active, and reverts the group when a redeem returns `state.ErrArbTxFilter`. Clean groups are finalized after tentative processing succeeds.

# Why It Matters

1. Prevents sequencer production and replay from disagreeing on auto-redeem execution.

2. Protects deterministic state-root calculation in this block-processing path.

3. Avoids committing partial effects from a user transaction whose generated redeem was filtered.

4. Evidence supports consensus divergence, not theft, auth bypass, or arbitrary state corruption.

# Evidence Notes

The strongest evidence is in `arbos/block_processor.go`: added `groupCheckpoint` state around line 267, checkpoint creation before user transactions around line 357, redeem filtering with deferred finalization context around line 471, group revert on `state.ErrArbTxFilter` around line 516, and final deferred `Finalise` flush around line 639. The commit body supplies the explicit replay-divergence scenario and design rationale. Detailed line-level evidence for delayed sequencer reporting, transaction-filterer behavior, and refund-drain handling was not included, so those should not be treated as independently verified here. Protocol security invariant: Block production and replay must deterministically derive the same block contents, receipts, gas accounting, and state root. A retryable auto-redeem filtered during sequencing must not be regenerated and executed during replay under different hook behavior. Verification notes: The patch proves a consensus divergence fix, not arbitrary state corruption outside this block production path. The evidence does not prove remote exploitability or attacker cost conditions. The evidence does not show theft, unauthorized balance transfer, or signature/authentication bypass. The delayed sequencer and transaction-filterer behavior is described by the commit body, but detailed line-level evidence is not provided here. The classification relies on the provided patch context and commit message, not external advisory status. Confirmed by provided commit message and focused block-processor hunks. No evidence provided for remote exploitability or attacker cost. No evidence provided for theft, authorization bypass, or arbitrary state corruption beyond the consensus-divergence path. Delayed-path behavior is described by the commit body but not substantiated by included code hunks. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `consensus-divergence`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, consensus-divergence, state-integrity, determinism`

The supplied commit metadata and patch evidence support a real consensus-integrity bug in a blockchain-core transaction-processing path, not just routine reliability work. The commit explicitly describes a sequencer-versus-replay state-root divergence when a retryable auto-redeem touches a filtered address, and the code changes implement grouped snapshot, deferred finalization, and whole-group revert logic to prevent that divergent execution. That is strong enough to keep this as a security-relevant fix, but the original bug class of generic state corruption is too broad, so a narrower consensus-divergence classification is more accurate.

## Security Evidence

1. Commit body explicitly states that dropping the redeem caused consensus divergence and a different state root during replay.
2. Patch adds a group-level state snapshot before each user transaction so the user tx and generated redeems are handled atomically.
3. Patch reverts the entire group when a redeem triggers state.ErrArbTxFilter, preventing partial execution that could differ across sequencing and replay.
4. Patch defers statedb.Finalise while a group checkpoint is active, showing the fix is aimed at preserving reversible consensus-sensitive state transitions.
5. Patch flushes deferred finalization only after a clean group completes, reinforcing deterministic block/state processing semantics.

## Missing Evidence

1. No included evidence shows how reachable or attacker-triggerable the filtered-address condition is in practice.
2. No included test hunk or runtime trace demonstrates the divergence before and after the fix.
3. No evidence here quantifies whether impact is limited to liveness/consensus safety or could escalate beyond state-root mismatch.

## Claim Boundaries

1. Evidence supports a consensus and state-determinism flaw in block production/replay handling for retryable auto-redeems.
2. Evidence does not support claims of theft, authentication bypass, memory corruption, or arbitrary state corruption outside this execution path.
3. Exploitability, attacker cost, and real-world exposure are not proven by the supplied patch alone.
4. The conservative validated class is consensus divergence affecting state integrity, not a broader corruption label.
