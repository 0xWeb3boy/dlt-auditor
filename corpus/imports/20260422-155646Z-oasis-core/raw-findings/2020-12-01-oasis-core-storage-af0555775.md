---
case_id: case_20201201_af0555775
project: oasis-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: security-hardening
phase3_keep_candidate: false
subsystem: storage
source_quality: high
date: 2020-12-01
source_refs:
  - git:af05557759864247296bae9739b335f158e2697c
  - "go/oasis-node/cmd/debug/txsource/workload/oversized.go:125"
  - "go/consensus/tendermint/abci/mux.go:615"
  - "go/oasis-test-runner/oasis/args.go:125"
  - "go/consensus/tendermint/abci/mux.go:1053"
bug_class: validation-bypass
impact_type:
  - mempool-validation-bypass
  - invalid-transaction-acceptance
confidence: medium
tags:
  - consensus
  - validator
  - mempool
  - checktx
  - debug-option
  - defense-in-depth
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The evidence supports that a debug-only `DisableCheckTx` path was removed from the Tendermint ABCI admission flow, along with supporting test/debug plumbing. That is security-relevant hardening of a consensus-sensitive validation path, but the provided patch does not establish an actual exploitable vulnerability in deployed configurations.

## Observed Patch Facts

1. In `go/oasis-node/cmd/debug/txsource/workload/oversized.go`, the patch replaces `// Timeout is expected if the client node skips CheckTx checks.` with `return fmt.Errorf("failed to submit oversized transaction: %w", err)`.

2. In `go/consensus/tendermint/abci/mux.go`, the patch replaces `if mux.state.disableCheckTx {` with `ctx := mux.state.NewContext(api.ContextCheckTx, mux.currentTime)`.

3. In `go/oasis-test-runner/oasis/args.go`, the patch replaces `func (args *argBuilder) tendermintDebugDisableCheckTx(disable bool) *argBuilder {` with `func (args *argBuilder) tendermintRecoverCorruptedWAL(enable bool) *argBuilder {`.

4. In `go/consensus/tendermint/abci/mux.go`, the patch replaces `// Create a map of expiring transactions if CheckTx is disabled (debug only).` with `"block_height", state.BlockHeight(),`.

## Project Context

The changed code sits primarily in `go/oasis-node/cmd/debug/txsource/workload`, `go/oasis-node/cmd/debug/txsource`, `go/consensus/tendermint/abci`, which anchors the finding in the `storage` area of the project. Historical context from `go/consensus/tendermint/abci/state.go`, `go/oasis-test-runner/oasis/fixture.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `go/oasis-test-runner/oasis/fixture.go`, `go/consensus/tendermint/full/full.go`. The strongest project-level identifiers around this patch are `args`, `transactions`, `transaction`, and `CheckTx`. Nearby tests or test-like files include `go/oasis-test-runner/scenario/e2e/seed_api.go`, `go/oasis-test-runner/scenario/e2e/runtime/storage_sync.go`.

## Before/After Behavior

Before the patch, `CheckTx` had a `disableCheckTx` branch that explicitly blind-accepted transactions and tracked them in debug-only expiry state, and test/debug code tolerated submission behavior consistent with skipped `CheckTx`. After the patch, `CheckTx` proceeds through the normal context-based execution path, the debug expiry support is removed, the test-runner flag for disabling `CheckTx` is removed, and the oversized transaction workload now treats unexpected submission failures as errors instead of tolerating skipped-check behavior.

# Root Cause

A debug-only configuration path existed inside the `CheckTx` admission entrypoint, allowing normal admission validation to be bypassed when locally enabled. The supplied evidence shows that this bypass mechanism was removed, but it does not show that the option was reachable by attackers, used in production, or led to invalid transactions being finalized.

## Walkthrough

1. `go/consensus/tendermint/abci/mux.go` removed a `disableCheckTx` branch whose comment said it would blindly accept transactions, which is direct evidence of a local validation-bypass mode.

2. The same file no longer initializes `debugExpiringTxs`, indicating that supporting state existed only for that bypass behavior and was removed with it.

3. `go/oasis-test-runner/oasis/args.go` deleted the helper that exposed the debug disable-`CheckTx` flag in the test harness, showing the configuration surface was intentionally removed.

4. `go/oasis-node/cmd/debug/txsource/workload/oversized.go` no longer treats a timeout from skipped `CheckTx` as acceptable and now returns an error for unexpected submission failures, reinforcing that bypassed admission is no longer expected.

5. These changes support a hardening claim around `CheckTx` validation, but the patch alone does not prove a concrete, exploitable security defect.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| go/consensus/tendermint/abci/mux.go | 615 | ABCI `CheckTx` entrypoint; debug path that blindly accepted transactions is removed so normal validation always runs |
| go/consensus/tendermint/abci/mux.go | 1053 | ABCI mux initialization no longer creates debug state used to retain transactions accepted without `CheckTx` validation |
| go/oasis-test-runner/oasis/args.go | 125 | test harness/CLI support for the unsafe `DisableCheckTx` option is removed |
| go/oasis-node/cmd/debug/txsource/workload/oversized.go | 125 | regression-style workload now treats failure to reject oversized transactions as an error instead of tolerating timeout from skipped checks |

## Code Snippets

## Snippet 1

Context: `go/oasis-node/cmd/debug/txsource/workload/oversized.go:125` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
o.Logger.Info("transaction rejected due to ErrOversizedTx")
		default:
			// Timeout is expected if the client node skips CheckTx checks.
			o.Logger.Warn("failed to submit oversized transaction",
				"err", err,
			)
		}
		cancel()
```
After
```go
o.Logger.Info("transaction rejected due to ErrOversizedTx")
		default:
			return fmt.Errorf("failed to submit oversized transaction: %w", err)
		}

		select {
```

## Snippet 2

Context: `go/consensus/tendermint/abci/mux.go:615` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
func (mux *abciMux) CheckTx(req types.RequestCheckTx) types.ResponseCheckTx {
	if mux.state.disableCheckTx {
		// Blindly accept all transactions if configured to do so. We still need to periodically
		// remove old transactions as otherwise the mempool will fill up, so keep track of when
		// transactions were added and invalidate them after the configured interval.
		txHash := hash.NewFromBytes(req.Tx)
```
After
```go
func (mux *abciMux) CheckTx(req types.RequestCheckTx) types.ResponseCheckTx {
	ctx := mux.state.NewContext(api.ContextCheckTx, mux.currentTime)
	defer ctx.Close()
```

## Snippet 3

Context: `go/oasis-test-runner/oasis/args.go:125` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

func (args *argBuilder) tendermintDebugDisableCheckTx(disable bool) *argBuilder {
	if disable {
		args.vec = append(args.vec, "--"+tendermintFull.CfgDebugDisableCheckTx)
	}
	return args
}
```
After
```go
}

func (args *argBuilder) tendermintRecoverCorruptedWAL(enable bool) *argBuilder {
	if enable {
```

## Snippet 4

Context: `go/consensus/tendermint/abci/mux.go:1053` (changes how canonical state is encoded, returned, or reconstructed)

Before
```go
}

	// Create a map of expiring transactions if CheckTx is disabled (debug only).
	if state.disableCheckTx {
		mux.debugExpiringTxs = make(map[hash.Hash]time.Time)
	}

	mux.logger.Debug("ABCI multiplexer initialized",
```
After
```go
}

	mux.logger.Debug("ABCI multiplexer initialized",
		"block_height", state.BlockHeight(),
```

# Fix Pattern

Remove debug-only validation-bypass paths from security-sensitive entrypoints and delete the configuration and support code that exists only to sustain that bypass.

## How It Was Fixed

The patch removed the `disableCheckTx` special case from the ABCI mux `CheckTx` path, removed the related debug transaction-expiry state, removed test-runner support for enabling the option, and updated the oversized transaction workload to stop tolerating behavior caused by skipped `CheckTx`.

# Why It Matters

1. It narrows the chance of operators or test setups running with transaction admission checks bypassed.

2. It restores a clearer invariant for the mempool-facing `CheckTx` path.

3. It removes tooling support that normalized skipped-validation behavior.

4. The evidence does not show attacker reachability or confirmed on-chain impact.

# Evidence Notes

The strongest evidence is the deleted `disableCheckTx` branch in `go/consensus/tendermint/abci/mux.go`, the removal of `debugExpiringTxs` setup, the deletion of the test-runner argument builder for the unsafe flag, and the oversized workload no longer tolerating skipped `CheckTx`. Unsupported stronger claims include production exposure, remote exploitability, cryptographic failure, or proof that invalid transactions could be finalized. Protocol security invariant: Transactions submitted through the Tendermint/ABCI mempool path should undergo normal `CheckTx` admission validation instead of being accepted via a local bypass mode. Verification notes: The patch does not prove the unsafe option was enabled in normal production deployments. The patch does not prove a remote attacker could toggle this option or reach it without operator misconfiguration. The patch does not show that invalid transactions could be finalized on-chain; it shows admission checks could be skipped at `CheckTx` time. The patch does not indicate a cryptographic break or signature-verification flaw. Evidence supports security-relevant hardening, not a confirmed vulnerability fix. No provided diff demonstrates that the debug option was enabled in production deployments. No provided diff demonstrates attacker-controlled activation of the bypass. No provided diff demonstrates block inclusion or finalization of invalid transactions. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `validation-bypass`
Final impact type: `mempool-validation-bypass, invalid-transaction-acceptance`
Final confidence: `medium`
Final tags: `consensus, validator, mempool, checktx, debug-option, defense-in-depth`

The patch clearly removes a debug-only path in the consensus `CheckTx` handler that would "blindly accept all transactions" and deletes the related configuration and support code. That is strong evidence of security hardening in a security-sensitive admission path. However, the provided diff does not prove attacker reachability, production exposure, or that invalid transactions could be finalized, so this should be retained as a hardening case rather than a confirmed vulnerability fix.

## Security Evidence

1. `CheckTx` no longer branches on `disableCheckTx` and instead always creates a normal check context.
2. The removed branch explicitly said it would "blindly accept all transactions if configured to do so."
3. Supporting state for expiring transactions accepted under the debug bypass was removed from ABCI mux initialization.
4. Test-runner argument support for the unsafe `DisableCheckTx` option was deleted.
5. The oversized transaction workload stopped tolerating behavior caused by skipped `CheckTx` and now treats it as an error.

## Missing Evidence

1. No proof that remote attackers could enable `DisableCheckTx`.
2. No proof that this option was reachable or enabled in production deployments.
3. No proof that blindly accepted transactions would be included in blocks or finalized on-chain.
4. No proof of a concrete exploit, signature bypass, or consensus break caused by this path.

## Claim Boundaries

1. Supported claim: the commit removes an unsafe debug validation-bypass mode from a consensus-sensitive transaction admission path.
2. Supported claim: this is security-relevant hardening / defense in depth.
3. Unsupported claim: a remotely exploitable security vulnerability was definitively fixed.
4. Unsupported claim: the patch proves state corruption, consensus divergence, or finalized invalid transactions.
