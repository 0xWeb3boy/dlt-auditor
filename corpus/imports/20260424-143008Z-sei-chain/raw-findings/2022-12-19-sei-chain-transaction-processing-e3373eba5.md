---
case_id: case_20221219_e3373eba5
project: sei-chain
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: liveness-failure
impact_type:
  - liveness
confidence: medium
source_quality: high
tags:
  - blockchain-core
  - transaction-processing
  - liveness-failure
  - liveness
date: 2022-12-19
source_refs:
  - git:e3373eba5afd2146395210eaea43df4fb9d8f35f
  - "x/dex/keeper/utils/wasm.go:40"
  - "x/dex/keeper/utils/wasm.go:55"
  - "x/oracle/simulation/operations.go:66"
  - "x/oracle/simulation/operations.go:123"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported security-relevant change is in x/dex/keeper/utils/wasm.go. The patch replaces an infinite temporary gas meter used for Wasm sudo execution with a gas meter derived from the parent context limit, and wraps the sudo call to recover sdk.ErrorOutOfGas panics while re-panicking other panics. This supports a likely liveness/resource-exhaustion hardening classification. The oracle simulation changes are comment formatting only.

## Observed Patch Facts

1. In `x/dex/keeper/utils/wasm.go`, the patch replaces `tmpCtx := sdkCtx.WithGasMeter(sdk.NewInfiniteGasMeter())` with `// Note that the limit will effectively serve as a soft limit since it's`.

2. In `x/dex/keeper/utils/wasm.go`, the patch replaces `func hasErrInstantiatingWasmModuleDueToCPUFeature(err error) bool {` with `func sudoWithoutOutOfGasPanic(ctx sdk.Context, k *keeper.Keeper, contractAddress []by...`.

3. In `x/oracle/simulation/operations.go`, the patch replaces `//nolint: funlen` with `// nolint: funlen`.

4. In `x/oracle/simulation/operations.go`, the patch replaces `//nolint: funlen` with `// nolint: funlen`.

## Project Context

The changed code sits primarily in `x/dex/keeper/utils`, `x/dex/keeper`, `x/oracle/simulation`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/oracle/simulation/genesis.go`, `x/oracle/simulation/params.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/dex/keeper/abci/end_block_place_orders.go`, `x/dex/keeper/abci/end_block_cancel_orders.go`. The strongest project-level identifiers around this patch are `tmpCtx`, `sdkCtx`, `nolint`, and `funlen`. Nearby tests or test-like files include `x/dex/keeper/msgserver/msg_server_place_orders_fuzz_test.go`, `x/oracle/spec/README.md`.

## Before/After Behavior

Before the patch, sudo() created tmpCtx with sdk.NewInfiniteGasMeter(), called k.WasmKeeper.Sudo(), then charged consumed gas back to the parent sdkCtx after the call returned. After the patch, sudo() creates tmpCtx with sdk.NewGasMeter(sdkCtx.GasMeter().Limit()), calls sudoWithoutOutOfGasPanic(), records consumed gas, and charges it to the parent context only when gasConsumed > 0. The helper recovers sdk.ErrorOutOfGas panics and preserves other panics.

# Root Cause

The Wasm sudo execution boundary used an infinite temporary gas meter during DEX block lifecycle processing. That allowed contract execution to run without the immediate parent-context gas bound until after sudo returned, which is consistent with the commit's stated BeginBlock/EndBlock infinite-loop failure mode.

## Walkthrough

1. DEX block lifecycle paths are traced to the sudo helper in x/dex/keeper/utils/wasm.go.

2. Before the patch, sudo() used sdk.NewInfiniteGasMeter() for the temporary context passed to WasmKeeper.Sudo.

3. Gas was charged back to the parent SDK context only after the sudo call returned.

4. The commit message describes BeginBlock/EndBlock getting stuck in contract infinite loops, matching the risk created by unbounded temporary contract execution.

5. After the patch, the temporary context uses sdk.NewGasMeter(sdkCtx.GasMeter().Limit()).

6. The sudo call is routed through sudoWithoutOutOfGasPanic(), which recovers sdk.ErrorOutOfGas and re-panics other values.

7. The oracle simulation edits only change nolint comment formatting and do not affect the security analysis.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/dex/keeper/utils/wasm.go | 40 | sets the gas meter used while executing Wasm sudo during DEX block lifecycle processing |
| x/dex/keeper/utils/wasm.go | 55 | wraps WasmKeeper.Sudo to recover out-of-gas panics while preserving other panics |
| x/dex/keeper/abci/end_block_place_orders.go | 2 | traced DEX EndBlock caller context for contract-backed order placement |
| x/dex/keeper/abci/end_block_cancel_orders.go | 1 | traced DEX EndBlock caller context for contract-backed order cancellation |
| x/oracle/simulation/operations.go | 66 | non-security comment formatting change only |
| x/oracle/simulation/operations.go | 123 | non-security comment formatting change only |

## Code Snippets

## Snippet 1

Context: `x/dex/keeper/utils/wasm.go:40` (changes bounds, limits, or capacity handling)

Before
```go
defer metrics.MeasureSudoExecutionDuration(time.Now(), msgType)
	// set up a tmp context to prevent race condition in reading gas consumed
	tmpCtx := sdkCtx.WithGasMeter(sdk.NewInfiniteGasMeter())
	data, err := k.WasmKeeper.Sudo(
		tmpCtx, contractAddress, wasmMsg,
	)
	gasConsumed := tmpCtx.GasMeter().GasConsumed()
	sdkCtx.GasMeter().ConsumeGas(gasConsumed, "sudo")
```
After
```go
defer metrics.MeasureSudoExecutionDuration(time.Now(), msgType)
	// set up a tmp context to prevent race condition in reading gas consumed
	// Note that the limit will effectively serve as a soft limit since it's
	// possible for the actual computation to go above the specified limit, but
	// the associated contract would be charged corresponding rent.
	tmpCtx := sdkCtx.WithGasMeter(sdk.NewGasMeter(sdkCtx.GasMeter().Limit()))
	data, err := sudoWithoutOutOfGasPanic(tmpCtx, k, contractAddress, wasmMsg)
	gasConsumed := tmpCtx.GasMeter().GasConsumed()
```

## Snippet 2

Context: `x/dex/keeper/utils/wasm.go:55` (changes a sensitive control or state-update path)

Before
```go
}

func hasErrInstantiatingWasmModuleDueToCPUFeature(err error) bool {
	if err == nil {
```
After
```go
}

func sudoWithoutOutOfGasPanic(ctx sdk.Context, k *keeper.Keeper, contractAddress []byte, wasmMsg []byte) ([]byte, error) {
	defer func() {
		if err := recover(); err != nil {
			// only propagate panic if the error is out of gas
			if _, ok := err.(sdk.ErrorOutOfGas); !ok {
				panic(err)
```

## Snippet 3

Context: `x/oracle/simulation/operations.go:66` (changes a sensitive control or state-update path)

Before
```go
// SimulateMsgAggregateExchangeRateVote generates a MsgAggregateExchangeRateVote with random values.
//nolint: funlen
func SimulateMsgAggregateExchangeRateVote(ak types.AccountKeeper, bk types.BankKeeper, k keeper.Keeper) simtypes.Operation {
	return func(
```
After
```go
// SimulateMsgAggregateExchangeRateVote generates a MsgAggregateExchangeRateVote with random values.
// nolint: funlen
func SimulateMsgAggregateExchangeRateVote(ak types.AccountKeeper, bk types.BankKeeper, k keeper.Keeper) simtypes.Operation {
	return func(
```

## Snippet 4

Context: `x/oracle/simulation/operations.go:123` (changes a sensitive control or state-update path)

Before
```go
// SimulateMsgDelegateFeedConsent generates a MsgDelegateFeedConsent with random values.
//nolint: funlen
func SimulateMsgDelegateFeedConsent(ak types.AccountKeeper, bk types.BankKeeper, k keeper.Keeper) simtypes.Operation {
	return func(
```
After
```go
// SimulateMsgDelegateFeedConsent generates a MsgDelegateFeedConsent with random values.
// nolint: funlen
func SimulateMsgDelegateFeedConsent(ak types.AccountKeeper, bk types.BankKeeper, k keeper.Keeper) simtypes.Operation {
	return func(
```

# Fix Pattern

Replace infinite metering in lifecycle-triggered Wasm execution with parent-limit-based gas metering, and handle expected out-of-gas panics at the Wasm sudo boundary.

## How It Was Fixed

x/dex/keeper/utils/wasm.go changed tmpCtx from sdk.NewInfiniteGasMeter() to sdk.NewGasMeter(sdkCtx.GasMeter().Limit()). The direct WasmKeeper.Sudo call was replaced with sudoWithoutOutOfGasPanic(), which recovers sdk.ErrorOutOfGas panics and re-panics non-out-of-gas panics. Parent gas charging remains after execution, guarded by gasConsumed > 0.

# Why It Matters

1. BeginBlock and EndBlock are liveness-sensitive protocol paths.

2. Infinite gas metering around contract execution can undermine resource limits during block processing.

3. Out-of-gas should be handled as an expected bounded failure, not an unhandled panic.

4. The evidence supports liveness/resource-exhaustion risk, not confidentiality or integrity impact.

# Evidence Notes

The strongest evidence is the wasm.go diff replacing sdk.NewInfiniteGasMeter() with sdk.NewGasMeter(sdkCtx.GasMeter().Limit()), adding a soft-limit comment, and introducing sudoWithoutOutOfGasPanic(). The commit subject explicitly names Begin/EndBlock being stuck in contract infinite loops. Traced contexts connect the helper to DEX EndBlock order placement and cancellation paths, but the supplied evidence does not prove exact external triggerability, permissions, or exploit mechanics. The oracle simulation hunks are non-security formatting changes. Protocol security invariant: Wasm sudo execution invoked from DEX BeginBlock/EndBlock paths should be constrained by the surrounding SDK context gas budget and should surface expected out-of-gas conditions without leaving block lifecycle processing stuck. Verification notes: The patch does not prove remote exploitability by itself. The patch does not show which contract messages or permissions can trigger the path. The oracle simulation edits are not security-relevant. The gas limit is described as a soft limit, so exact runtime bounds are not fully proven from the patch alone. The evidence supports liveness/resource exhaustion risk, not confidentiality or integrity impact. Verified by provided diff evidence only; no independent file inspection was performed. Remote exploitability is not established by the supplied evidence. Classification is likely security hardening rather than a fully confirmed vulnerability fix. Helper additions are support code for the Wasm sudo boundary, not a separate root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The supplied patch evidence supports retaining this as security hardening rather than a confirmed vulnerability fix. The core change removes an infinite gas meter around Wasm sudo execution in BeginBlock/EndBlock-related DEX logic, replaces it with a parent-limit-based gas meter, and handles out-of-gas panics at that boundary. That is a resource-control tightening in a liveness-sensitive blockchain path, and the commit message explicitly references Begin/EndBlock getting stuck in contract infinite loops. The evidence does not prove exploitability, permissions, or a concrete external attack path, so security-fix would be too strong.

## Security Evidence

1. Replaces sdk.NewInfiniteGasMeter() with sdk.NewGasMeter(sdkCtx.GasMeter().Limit()) for Wasm sudo execution.
2. Adds handling for sdk.ErrorOutOfGas panics around k.WasmKeeper.Sudo while preserving other panics.
3. Commit subject names Begin/EndBlock stuck in contract infinite loops, matching a liveness/resource-exhaustion concern.
4. Changed code is in DEX keeper Wasm utility code tied to block lifecycle execution paths.

## Missing Evidence

1. No direct proof of external attacker triggerability is supplied.
2. No test evidence demonstrates a malicious or untrusted contract causing chain halt or block processing denial of service.
3. The gas limit is described as a soft limit, so exact runtime containment is not fully proven from the patch alone.
4. Oracle simulation changes are comment formatting only and provide no security evidence.

## Claim Boundaries

1. Classify as security-hardening, not confirmed security-fix.
2. Supported impact is liveness/resource exhaustion only, not confidentiality or integrity.
3. Do not treat oracle simulation formatting edits as part of the security fix.
4. Do not claim a specific exploit path beyond contract execution in BeginBlock/EndBlock-sensitive Wasm sudo handling.
