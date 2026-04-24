---
case_id: case_20251029_48090d81b
project: sei-chain
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: confirmed
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: high
date: 2025-10-29
source_refs:
  - git:48090d81b8e158761f0161f1ac386007ed6e31ea
  - "x/evm/ante/sig.go:69"
  - "sei-cosmos/baseapp/baseapp.go:910"
  - "sei-cosmos/baseapp/baseapp.go:1012"
  - "sei-cosmos/baseapp/baseapp.go:981"
bug_class: mempool-nonce-bookkeeping
impact_type:
  - transaction-ordering-integrity
confidence: medium
tags:
  - transaction-processing
  - mempool
  - evm
  - nonce-ordering
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

This patch fixes stale EVM pending-nonce bookkeeping in the CheckTx/mempool admission path. Before the fix, a transaction nonce could be recorded in the pending-nonce tracker before the transaction was actually accepted into active or pending mempool, and some later rejection paths did not roll that nonce back. That stale nonce could make a higher-nonce transaction appear eligible for promotion and block inclusion.

## Observed Patch Facts

1. In `x/evm/ante/sig.go`, the patch replaces `ctx = ctx.WithCheckTxCallback(func(thenCtx sdk.Context, e error) {` with `ctx = ctx.WithCheckTxCallback(func(priority int64) {`.

2. In `sei-cosmos/baseapp/baseapp.go`, the patch replaces `return sdk.GasInfo{}, nil, nil, 0, nil, nil, ctx, sdkerrors.Wrap(sdkerrors.ErrTxDecod...` with `return sdk.GasInfo{}, nil, nil, 0, nil, nil, nil, ctx, sdkerrors.Wrap(sdkerrors.ErrTx...`.

3. In `sei-cosmos/baseapp/baseapp.go`, the patch removes `if ctx.CheckTxCallback() != nil {`.

4. In `sei-cosmos/baseapp/baseapp.go`, the patch replaces `return gInfo, nil, nil, 0, nil, nil, ctx, sdkerrors.Wrap(sdkerrors.ErrInvalidConcurre...` with `return gInfo, nil, nil, 0, nil, nil, nil, ctx, sdkerrors.Wrap(sdkerrors.ErrInvalidCon...`.

## Project Context

The changed code sits primarily in `x/evm/ante`, `x/evm`, `sei-cosmos/baseapp`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sei-cosmos/baseapp/deliver_tx_batch_test.go`, `sei-cosmos/baseapp/p2p.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sei-cosmos/baseapp/deliver_tx_batch_test.go`, `sei-cosmos/baseapp/p2p.go`. The strongest project-level identifiers around this patch are `sdkerrors`, `error`, `Wrap`, and `txKey`. Nearby tests or test-like files include `x/evm/integration_test.go`, `x/evm/blocktest/config.go`.

## Before/After Behavior

Before the patch, the EVM ante handler registered a CheckTx callback taking sdk.Context and error, and BaseApp invoked ctx.CheckTxCallback()(ctx, err) from runTx when runTx completed. The commit context states this allowed pending-nonce insertion before final active or pending mempool inclusion, with incomplete rollback on later failures. After the patch, the callback takes only a priority, BaseApp no longer directly invokes the callback inside runTx, and runTx returns the callback separately so it can be applied by the mempool path after successful admission.

# Root Cause

Pending-nonce bookkeeping was tied to runTx completion rather than to final mempool admission. Because not every later mempool rejection path invoked rollback, a rejected transaction could leave its nonce in the pending-nonce tracker.

## Walkthrough

1. An EVM CheckTx transaction with nonce N can register a callback that will add N to the pending-nonce tracker.

2. Before the fix, BaseApp invoked that callback from runTx based on the execution error state, before all mempool admission failure paths had completed.

3. If the transaction was later rejected from active or pending mempool and rollback was missed, nonce N could remain in the pending-nonce index.

4. A pending transaction with nonce N+1 could then appear to have its nonce gap filled.

5. The commit states that mempool.Update uses state nonce plus pending nonces for promotion decisions, so the stale N entry could promote N+1 to active mempool and make it block-eligible.

6. The fix changes the callback interface and removes BaseApp's direct callback invocation, allowing nonce insertion only from the later acceptance path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/ante/sig.go | 69 | Registers the EVM CheckTx callback that adds an accepted transaction nonce to the pending-nonce tracker. |
| sei-cosmos/baseapp/baseapp.go | 855 | Extends runTx return values to carry the CheckTx callback separately instead of executing it inside runTx. |
| sei-cosmos/baseapp/baseapp.go | 1006 | Removes BaseApp's direct callback invocation after transaction execution, preventing nonce recording before final mempool acceptance. |
| sei-tendermint/internal/mempool/mempool.go | 303 | Business-logic path described by the commit where CheckTx adds pending nonces used for later promotion decisions. |
| sei-tendermint/internal/mempool/mempool.go | 634 | Promotion path described by the commit where pending nonces can make gap transactions eligible for active mempool inclusion. |

## Code Snippets

## Snippet 1

Context: `x/evm/ante/sig.go:69` (changes a sensitive control or state-update path)

Before
```go
return ctx, sdkerrors.ErrWrongSequence
		}
		ctx = ctx.WithCheckTxCallback(func(thenCtx sdk.Context, e error) {
			if e != nil {
				return
			}
			txKey := tmtypes.Tx(ctx.TxBytes()).Key()
			svd.evmKeeper.AddPendingNonce(txKey, evmAddr, txNonce, thenCtx.Priority())
```
After
```go
return ctx, sdkerrors.ErrWrongSequence
		}
		ctx = ctx.WithCheckTxCallback(func(priority int64) {
			txKey := tmtypes.Tx(ctx.TxBytes()).Key()
			svd.evmKeeper.AddPendingNonce(txKey, evmAddr, txNonce, priority)
			metrics.IncrementPendingNonce("added")
		})
```

## Snippet 2

Context: `sei-cosmos/baseapp/baseapp.go:910` (changes persisted or aggregate state handling)

Before
```go
if tx == nil {
		return sdk.GasInfo{}, nil, nil, 0, nil, nil, ctx, sdkerrors.Wrap(sdkerrors.ErrTxDecode, "tx decode error")
	}
```
After
```go
if tx == nil {
		return sdk.GasInfo{}, nil, nil, 0, nil, nil, nil, ctx, sdkerrors.Wrap(sdkerrors.ErrTxDecode, "tx decode error")
	}
```

## Snippet 3

Context: `sei-cosmos/baseapp/baseapp.go:1012` (changes a sensitive control or state-update path)

Before
```go
result.Events = append(anteEvents, result.Events...)
	}
	if ctx.CheckTxCallback() != nil {
		ctx.CheckTxCallback()(ctx, err)
	}
	// only apply hooks if no error
	if err == nil && (!ctx.IsEVM() || result.EvmError == "") {
```
After
```go
result.Events = append(anteEvents, result.Events...)
	}
	// only apply hooks if no error
	if err == nil && (!ctx.IsEVM() || result.EvmError == "") {
```

## Snippet 4

Context: `sei-cosmos/baseapp/baseapp.go:981` (changes a sensitive control or state-update path)

Before
```go
}
				errMessage := fmt.Sprintf("Invalid Concurrent Execution antehandler missing %d access operations", len(missingAccessOps))
				return gInfo, nil, nil, 0, nil, nil, ctx, sdkerrors.Wrap(sdkerrors.ErrInvalidConcurrencyExecution, errMessage)
			}
		}
```
After
```go
}
				errMessage := fmt.Sprintf("Invalid Concurrent Execution antehandler missing %d access operations", len(missingAccessOps))
				return gInfo, nil, nil, 0, nil, nil, nil, ctx, sdkerrors.Wrap(sdkerrors.ErrInvalidConcurrencyExecution, errMessage)
			}
		}
```

# Fix Pattern

Move side-effectful nonce bookkeeping to the same acceptance boundary represented by that bookkeeping, instead of inserting early and relying on rollback across later failure paths.

## How It Was Fixed

The EVM CheckTx callback was changed from func(sdk.Context, error) to func(int64), using an explicit priority when AddPendingNonce is called. BaseApp's runTx now carries the callback as a separate return value and early error paths return nil for it. The direct ctx.CheckTxCallback()(ctx, err) invocation inside runTx was removed, so pending nonces are not added from the generic runTx completion point.

# Why It Matters

1. Preserves EVM account nonce ordering during mempool promotion.

2. Prevents rejected transactions from leaving nonce state that influences later transaction eligibility.

3. Keeps the pending-nonce index aligned with actual pending or active mempool contents.

4. Reduces reliance on incomplete rollback coverage across mempool failure paths.

5. Evidence supports a mempool nonce-ordering vulnerability, not signature forgery or proven consensus divergence.

# Evidence Notes

The strongest evidence is x/evm/ante/sig.go changing the CheckTx callback from func(sdk.Context, error) to func(int64), and sei-cosmos/baseapp/baseapp.go removing the direct ctx.CheckTxCallback()(ctx, err) invocation while adding a separate checkTxCallback return. The commit message gives the specific failure scenario: a rejected nonce N can remain in pending nonces and cause N+1 promotion. The supplied evidence does not establish remote exploitability, economic loss, signature validation bypass, or consensus divergence. Protocol security invariant: For EVM transactions, mempool promotion must not treat an account nonce gap as filled unless the gap-filling transaction has actually been accepted into pending or active mempool, because promotion and block eligibility depend on the pending-nonce index. Verification notes: The patch does not by itself prove remote exploitability or economic impact. The evidence does not show consensus divergence, only mempool admission and block-eligibility ordering risk. The evidence does not show signature forgery or chain-ID validation failure. The finding should not be classified primarily as replay-or-signature-validation despite touching the EVM signature ante handler. Commit message describes a reproduced gap-nonce issue and states the branch no longer reproduces it. Code evidence supports moving AddPendingNonce away from BaseApp runTx completion. No independent test output is provided in the input. No evidence supports classifying this as replay, signature forgery, or chain-ID validation failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `mempool-nonce-bookkeeping`
Final impact type: `transaction-ordering-integrity`
Final confidence: `medium`
Final tags: `transaction-processing, mempool, evm, nonce-ordering, security-hardening`

The evidence supports a security-relevant hardening/fix around EVM nonce-ordering behavior in the mempool: a rejected transaction could leave stale pending-nonce state that influenced promotion of a higher-nonce transaction. The commit message describes a concrete gap-nonce inclusion scenario, and the patch moves pending-nonce insertion away from generic runTx completion toward a later acceptance boundary. However, the supplied evidence does not prove replay, signature validation bypass, remote exploitability, economic impact, or consensus divergence, so the original classification is too specific and too strong.

## Security Evidence

1. Commit describes stale pending nonces remaining after mempool rejection because rollback was not invoked on all failure paths.
2. Commit scenario states nonce N+1 could be promoted and become block-eligible without nonce N being included first.
3. Patch changes the EVM CheckTx callback so AddPendingNonce is no longer called through the old runTx callback signature with error context.
4. Patch removes BaseApp's direct ctx.CheckTxCallback()(ctx, err) invocation from runTx.
5. runTx now carries a separate checkTxCallback return value, supporting delayed nonce bookkeeping after successful admission.

## Missing Evidence

1. No evidence of signature forgery, replay, or chain-ID validation bypass.
2. No proof that the issue caused accepted invalid blocks or consensus divergence.
3. No proof of remote exploitability, funds loss, or privilege escalation.
4. No test output or full mempool acceptance-path diff is provided to show the exact new callback invocation point.

## Claim Boundaries

1. Valid claim: stale pending-nonce bookkeeping could affect mempool promotion and nonce ordering.
2. Valid claim: the patch tightens when pending nonces are recorded relative to transaction admission.
3. Do not claim request forgery, replay, or signature-validation bypass from this evidence.
4. Do not claim confirmed consensus failure or economic impact from the supplied patch alone.
