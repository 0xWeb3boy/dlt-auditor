---
case_id: case_20260209_d9f1de1a4
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2026-02-09
source_refs:
  - git:d9f1de1a4de7b131bac065f86113ae2d153f12fe
  - "giga/executor/executor.go:48"
  - "app/app.go:1972"
  - "app/app.go:2009"
  - "app/app.go:1682"
bug_class: app-hash-state-accounting-inconsistency
impact_type:
  - liveness
tags:
  - blockchain
  - consensus
  - transaction-processing
  - state-accounting
  - app-hash
  - liveness
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports a likely security-relevant app-hash/state-accounting consistency fix in sei-chain's giga EVM execution path. The patch changes consensus-critical block-processing code to preserve `stateDB.Finalize()` surplus, pass that surplus into deferred EVM transaction info instead of hardcoding zero, and flush giga-store writes before later BankKeeper and EndBlock reads. The added fee-already-charged executor function is support for aligning giga execution with a path where ante handling already charged fees, but the provided evidence does not show its call site.

## Observed Patch Facts

1. In `giga/executor/executor.go`, the patch adds `// ExecuteTransactionFeeCharged executes a transaction assuming the gas fee has alrea...`.

2. In `app/app.go`, the patch replaces `// Finalize state changes` with `// Finalize state changes — single Finalize for both fee + execution.`.

3. In `app/app.go`, the patch replaces `// Append deferred info for EndBlock processing` with `// Append deferred info for EndBlock processing.`.

4. In `app/app.go`, the patch replaces `// Finalize all Bank Module Transfers here so that events are included for prioritiez...` with `// When using the giga executor via ProcessTxsSynchronousGiga, balance changes go thr...`.

## Project Context

The changed code sits primarily in `giga/executor`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `app/test_helpers.go`, `app/seidb.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `giga/executor/utils/errors.go`, `giga/executor/internal/host_context.go`. The strongest project-level identifiers around this patch are `surplus`, `Finalize`, `giga`, and `changes`.

## Before/After Behavior

Before the patch, `executeEVMTxWithGigaExecutor` called `stateDB.Finalize()` but discarded the returned surplus, then appended deferred EVM transaction info with `surplus := sdk.ZeroInt()`. After the patch, it captures the finalized surplus and passes it onward. Before the patch, `ProcessBlock` proceeded to deferred bank balance writes without the shown giga-store flush; after the patch, when `app.GigaExecutorEnabled` is true, it calls `ctx.GigaMultiStore().WriteGiga()` first. The patch also adds `ExecuteTransactionFeeCharged`, documented for transactions whose fee was already charged by ante handling.

# Root Cause

The supported root cause is inconsistent accounting and state visibility in the giga EVM block-processing path: finalized surplus was discarded, deferred EVM metadata received zero surplus, and giga-store writes were not shown as flushed before later standard bank and EndBlock processing read balances.

## Walkthrough

1. A block is processed through `ProcessBlock`, including paths that may use the giga executor when enabled.

2. Giga executor balance changes can live in giga-store layers before later bank and EndBlock processing.

3. The old shown path finalized EVM state but ignored the returned surplus.

4. The old deferred EVM info path hardcoded surplus to zero, losing the finalize accounting result.

5. The patch preserves the finalized surplus and passes it into deferred EVM transaction info.

6. The patch flushes giga-store writes before standard bank deferred balance handling and EndBlock reads.

7. The added fee-already-charged executor function documents support for matching V2-style ante fee charging, though the provided snippets do not prove where it is invoked.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| giga/executor/executor.go | 48 | Adds `ExecuteTransactionFeeCharged` so the giga EVM path can execute after ante fee charging without EVM-side fee charge/refund behavior diverging from V2. |
| app/app.go | 1972 | Captures the single `stateDB.Finalize()` surplus covering both fee deduction and execution balance changes. |
| app/app.go | 2009 | Passes the finalized surplus into deferred EVM transaction info used later in EndBlock instead of hardcoding zero. |
| app/app.go | 1682 | Flushes deliver-state giga stores before standard bank deferred balance writes and EndBlock so later reads observe the giga executor's balance changes. |

## Code Snippets

## Snippet 1

Context: `giga/executor/executor.go:48` (changes a sensitive control or state-update path)

Before
```go
return executionResult, nil
}
```
After
```go
return executionResult, nil
}

// ExecuteTransactionFeeCharged executes a transaction assuming the gas fee has already been charged
// (like V2's msg_server path where the ante handler charges fees separately).
// This ensures the EVM does NOT charge/refund gas fees during execution, matching V2's behavior
// where feeAlreadyCharged=true is passed to StateTransition.Execute().
func (e *Executor) ExecuteTransactionFeeCharged(tx *types.Transaction, sender common.Address, baseFee *big.Int, gasPool *core.GasPool) (*core.ExecutionResult, error) {
```

## Snippet 2

Context: `app/app.go:1972` (changes a consensus- or validator-sensitive branch)

Before
```go
}

	// Finalize state changes
	_, ferr := stateDB.Finalize()
	if ferr != nil {
		return &abci.ExecTxResult{
```
After
```go
}

	// Finalize state changes — single Finalize for both fee + execution.
	// The surplus includes the fee deduction (positive) plus any execution balance changes.
	surplus, ferr := stateDB.Finalize()
	if ferr != nil {
		return &abci.ExecTxResult{
```

## Snippet 3

Context: `app/app.go:2009` (changes aggregate state or economic accounting)

Before
```go
}

	// Append deferred info for EndBlock processing
	// Calculate surplus (gas fee paid minus gas used * effective gas price)
	// For giga executor, we set surplus to zero since we're not charging gas fees through the normal flow
	surplus := sdk.ZeroInt()
	bloom := ethtypes.Bloom{}
	bloom.SetBytes(receipt.LogsBloom)
```
After
```go
}

	// Append deferred info for EndBlock processing.
	// The surplus from the single Finalize includes both the fee deduction surplus and
	// any execution balance changes, equivalent to V2's anteSurplus + executionSurplus.
	bloom := ethtypes.Bloom{}
	bloom.SetBytes(receipt.LogsBloom)
```

## Snippet 4

Context: `app/app.go:1682` (changes aggregate state or economic accounting)

Before
```go
}

	// Finalize all Bank Module Transfers here so that events are included for prioritiezd txs
	deferredWriteEvents := app.BankKeeper.WriteDeferredBalances(ctx)
```
After
```go
}

	// When using the giga executor via ProcessTxsSynchronousGiga, balance changes go through
	// the giga KV store (via GigaBankKeeper). ProcessTxsSynchronousGiga flushes its cache-layer
	// giga stores to the deliver state's giga stores, but the deliver state's giga stores must
	// also be flushed so that subsequent operations (WriteDeferredBalances, EndBlock) that use
	// the standard BankKeeper can see the correct balances via read-through to the committed store.
	if app.GigaExecutorEnabled {
```

# Fix Pattern

Align an alternate execution path with canonical consensus accounting by preserving finalized deltas, propagating them to deferred metadata, and flushing alternate store layers before downstream state reads.

## How It Was Fixed

`app/app.go` now stores the surplus returned by `stateDB.Finalize()` and passes it to `AppendToEvmTxDeferredInfo`. `ProcessBlock` now flushes giga stores with `ctx.GigaMultiStore().WriteGiga()` when the giga executor is enabled. `giga/executor/executor.go` adds `ExecuteTransactionFeeCharged` for already-charged-fee execution semantics.

# Why It Matters

1. App-hash computation depends on deterministic state and metadata before EndBlock.

2. Discarding finalized surplus can lose consensus-relevant accounting information.

3. Hardcoding zero surplus can diverge from actual fee and execution balance deltas.

4. Unflushed giga-store writes can make later module reads observe stale balances.

5. The evidence supports app-hash/state consistency risk, not malformed-input panic or direct fund theft.

# Evidence Notes

The heuristic malformed-input panic theory is unsupported and should be rejected. The evidence does not establish remote exploitability, a crafted transaction trigger, fund theft, or exact validator-divergence conditions. The strongest evidence is the commit subject, consensus-path files, comments describing app-hash-relevant fee/surplus behavior, and changes in `ProcessBlock` and `executeEVMTxWithGigaExecutor`. Confidence is medium rather than high because the provided snippets do not include the full call graph, failing tests, or an explicit reproduction of app-hash divergence. Protocol security invariant: When the giga EVM executor is enabled, fee charging, finalized surplus propagation, deferred EVM metadata, and giga-store visibility must match the canonical block execution path before EndBlock/app-hash computation. Verification notes: The patch does not prove remote exploitability by a crafted transaction. The patch does not show a panic or unchecked conversion bug. The patch does not prove fund theft or fee bypass beyond inconsistent fee/surplus accounting in the giga path. The evidence does not identify whether all validators would diverge or whether the issue only caused local app-hash mismatch under specific configurations. The patch is specific to the giga executor / EVM block-processing path, not general transaction processing. No evidence of unchecked conversion or panic was provided. No direct exploit scenario was proven. No call site for `ExecuteTransactionFeeCharged` was included in the supplied evidence. The changed `app/app.go` paths are sufficient to support likely app-hash/state-accounting relevance. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `app-hash-state-accounting-inconsistency`
Final impact type: `liveness`
Final tags: `blockchain, consensus, transaction-processing, state-accounting, app-hash, liveness`

The supplied patch evidence supports retaining this as security hardening, not a proven security fix. The changes affect blockchain block-processing and EVM execution accounting, preserve finalized surplus instead of discarding it, propagate that surplus to deferred EVM info, and flush giga-store writes before later BankKeeper and EndBlock reads. That is plausibly app-hash and consensus-sensitive, but the evidence does not prove a concrete exploit, validator divergence trigger, or demonstrated liveness failure.

## Security Evidence

1. Commit subject explicitly references fixes for app hash.
2. Patch changes consensus-sensitive block processing in app/app.go.
3. stateDB.Finalize() surplus is now preserved instead of discarded.
4. Deferred EVM transaction info now receives finalized surplus instead of hardcoded zero.
5. Giga store writes are flushed before downstream BankKeeper and EndBlock reads.

## Missing Evidence

1. No failing test or reproduction showing app-hash mismatch is provided.
2. No concrete crafted transaction or attacker-controlled trigger is shown.
3. No evidence proves validator divergence conditions or network halt.
4. No direct fund theft, fee bypass exploit, or safety violation is demonstrated.
5. Call site evidence for ExecuteTransactionFeeCharged is not included.

## Claim Boundaries

1. Classify as security hardening because the patch tightens consensus/state-accounting behavior.
2. Do not claim a confirmed exploitable vulnerability from the supplied evidence alone.
3. Do not claim malformed-input panic, direct theft, or fee bypass.
4. Scope is limited to the giga EVM execution and block-processing path.
