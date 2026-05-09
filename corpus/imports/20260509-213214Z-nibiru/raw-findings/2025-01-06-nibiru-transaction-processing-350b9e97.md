---
case_id: case_20250106_350b9e97
project: nibiru
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2025-01-06
source_refs:
  - git:350b9e97c763ebf6edf0d896866bd6d1ac7e9c31
  - "x/evm/keeper/bank_extension.go:169"
  - "app/ante/fixed_gas_test.go:198"
  - "x/evm/keeper/bank_extension_test.go:62"
  - "x/evm/keeper/bank_extension_test.go:70"
bug_class: gas-accounting-undercharge
impact_type:
  - resource-accounting
  - resource-exhaustion-risk
tags:
  - transaction-processing
  - evm
  - bank
  - gas-accounting
  - resource-control
  - security-hardening
validation_status: completed
security_verdict: confirmed
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is a resource-accounting fix in `ForceGasInvariant`: the wrapper previously measured the wrapped bank operation using a substitute gas meter with zero-cost KV and transient KV gas configs, then charged the original transaction gas meter based on that reduced measurement. The patch replaces that setup with an infinite substitute gas meter and removes the zero-cost KV configs, and tests now require non-zero measured gas and expect a higher transaction gas total.

## Observed Patch Facts

1. In `x/evm/keeper/bank_extension.go`, the patch replaces `ctx = ctx.` with `// We use an infinite gas meter because we consume gas in the deferred function`.

2. In `app/ante/fixed_gas_test.go`, the patch replaces `expectedGas: 38175,` with `expectedGas: 67193,`.

3. In `x/evm/keeper/bank_extension_test.go`, the patch adds `s.T().Logf("gasConsumed: %d", gasConsumed)`.

4. In `x/evm/keeper/bank_extension_test.go`, the patch replaces `fmt.Sprintf("%d", first),` with `first,`.

## Project Context

The changed code sits primarily in `x/evm/keeper`, `x/evm`, `app/ante`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `x/evm/keeper/grpc_query.go`, `x/evm/keeper/gas_fees.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `x/evm/keeper/grpc_query.go`, `x/evm/keeper/gas_fees.go`. The strongest project-level identifiers around this patch are `gasConsumed`, `first`, `meter`, and `equal`. Nearby tests or test-like files include `x/evm/precompile/test/export.go`, `x/evm/evmtest/tx_test.go`.

## Before/After Behavior

Before the patch, `ForceGasInvariant` ran `BaseOp(ctx)` under `sdk.NewGasMeter(gasMeterBefore.Limit())` while applying `zeroCostGasConfig` to KV and transient KV accounting. The deferred charge to the original gas meter depended on `ctx.GasMeter().GasConsumed()`, so the measured amount could omit gas hidden by those zero-cost configs. After the patch, `BaseOp(ctx)` runs under `sdk.NewInfiniteGasMeter()` without those zero-cost gas config overrides, and the measured gas is charged back to the original transaction gas meter in the deferred function. Tests were updated to assert non-zero gas consumption and to expect a higher fixed gas value.

# Root Cause

The gas-invariant wrapper used a substitute measurement context that explicitly disabled KV and transient KV gas costs. Because the wrapper later charged the real transaction gas meter from the substitute meter's measured consumption, that setup could undercharge bank-operation gas.

## Walkthrough

1. `ForceGasInvariant` stores the original transaction gas meter and the gas consumed before the wrapped operation.

2. The function defers logic that refunds the original meter's current consumption and consumes `gasConsumedBefore + baseOpGasConsumed` on that original meter.

3. Before the fix, `BaseOp(ctx)` ran under a new capped gas meter with zero-cost KV and transient KV gas configs.

4. The measured `baseOpGasConsumed` therefore came from a context that could suppress some bank-operation gas accounting.

5. After the fix, the substitute context uses `sdk.NewInfiniteGasMeter()` and no longer installs the zero-cost KV gas configs.

6. The measured gas from the substitute meter is then applied back to the original transaction gas meter.

7. The bank extension test now requires the measured invariant gas to be non-zero.

8. The ante test expected gas increased from `38175` to `67193`, supporting that additional gas is now charged.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| x/evm/keeper/bank_extension.go | 148 | ForceGasInvariant wrapper captures pre-operation gas state, runs the bank operation under a substitute gas meter, then applies measured gas back to the transaction gas meter. |
| x/evm/keeper/bank_extension.go | 169 | Changed substitute gas meter setup from capped zero-cost KV accounting to an infinite gas meter using normal gas accounting. |
| x/evm/keeper/bank_extension_test.go | 62 | Test now asserts gas consumed by invariant scenarios is non-zero. |
| app/ante/fixed_gas_test.go | 198 | Expected transaction gas increased, reflecting newly charged bank-operation gas. |

## Code Snippets

## Snippet 1

Context: `x/evm/keeper/bank_extension.go:169` (changes bounds, limits, or capacity handling)

Before
```go
// we have to branch off with a new gas meter instance to avoid mutating the
	// "true" gas meter (called GasMeterBefore here).
	ctx = ctx.
		WithGasMeter(sdk.NewGasMeter(gasMeterBefore.Limit())).
		WithKVGasConfig(zeroCostGasConfig).
		WithTransientKVGasConfig(zeroCostGasConfig)

	err := BaseOp(ctx)
```
After
```go
// we have to branch off with a new gas meter instance to avoid mutating the
	// "true" gas meter (called GasMeterBefore here).
	// We use an infinite gas meter because we consume gas in the deferred function
	// and gasMeterBefore will panic if we consume too much gas.
	ctx = ctx.WithGasMeter(sdk.NewInfiniteGasMeter())

	err := BaseOp(ctx)
```

## Snippet 2

Context: `app/ante/fixed_gas_test.go:198` (changes a sensitive control or state-update path)

Before
```go
},
			},
			expectedGas: 38175,
			expectedErr: nil,
		},
```
After
```go
},
			},
			expectedGas: 67193,
			expectedErr: nil,
		},
```

## Snippet 3

Context: `x/evm/keeper/bank_extension_test.go:62` (changes the branch that decides whether execution stops or continues)

Before
```go
s.Run(tc.name, func() {
			gasConsumed := tc.GasConsumedInvariantScenario.Run(s, to)
			if idx == 0 {
				first = gasConsumed
```
After
```go
s.Run(tc.name, func() {
			gasConsumed := tc.GasConsumedInvariantScenario.Run(s, to)
			s.T().Logf("gasConsumed: %d", gasConsumed)
			s.Require().NotZerof(gasConsumed, "gasConsumed should not be zero")
			if idx == 0 {
				first = gasConsumed
```

## Snippet 4

Context: `x/evm/keeper/bank_extension_test.go:70` (changes a sensitive control or state-update path)

Before
```go
// Each elem being equal to "first" implies that each elem is equal
			s.Equalf(
				fmt.Sprintf("%d", first),
				fmt.Sprintf("%d", gasConsumed),
				"Gas consumed should be equal",
			)
```
After
```go
// Each elem being equal to "first" implies that each elem is equal
			s.Equalf(
				first,
				gasConsumed,
				"Gas consumed should be equal",
			)
```

# Fix Pattern

Measure the wrapped operation on a separate gas meter without disabling relevant gas accounting, then apply the measured amount back to the real transaction gas meter at the controlled accounting boundary.

## How It Was Fixed

The patch removed the substitute context chain using `sdk.NewGasMeter(gasMeterBefore.Limit())`, `WithKVGasConfig(zeroCostGasConfig)`, and `WithTransientKVGasConfig(zeroCostGasConfig)`. It now uses `ctx.WithGasMeter(sdk.NewInfiniteGasMeter())`. Tests were updated to assert non-zero measured gas, compare numeric gas values directly, and reflect the higher expected gas total.

# Why It Matters

1. Transaction gas accounting is a resource-control mechanism.

2. Undercharging bank-operation work can let transactions consume more execution resources than they pay for.

3. The evidence supports gas undercharging, not malformed-input panic, authorization bypass, balance theft, or a proven denial-of-service exploit.

4. The concrete exploitability and impact are not established by the provided evidence.

# Evidence Notes

The strongest evidence is the focused change in `x/evm/keeper/bank_extension.go`, where zero-cost KV gas configs were removed from the substitute measurement context, plus tests adding a non-zero gas assertion and increasing an expected gas value. Claims about malformed transaction decoding, panic-on-conversion, remote crashes, consensus failure, or direct fund loss are unsupported and removed. Protocol security invariant: Bank operations executed through the EVM bank extension should have their measured gas charged back to the real transaction gas meter instead of being measured under a context that suppresses relevant KV gas costs. Verification notes: No evidence of malformed transaction decoding or panic-on-conversion behavior is shown. No concrete exploit path, remote denial of service, or consensus divergence is proven by the patch alone. No authorization, balance theft, or signature validation bypass is indicated. The infinite gas meter change is part of deferred accounting and does not by itself prove unbounded free execution after the final charge is applied. Verified from supplied evidence only; no external files or commands were used. Patch behavior is supported at the gas-accounting level. Exploitability beyond resource undercharging is not proven by the provided evidence. Confidence is medium rather than high because the evidence shows undercharging but not a concrete attack path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `gas-accounting-undercharge`
Final impact type: `resource-accounting, resource-exhaustion-risk`
Final tags: `transaction-processing, evm, bank, gas-accounting, resource-control, security-hardening`

The supplied patch clearly fixes gas accounting in a transaction-processing path: `ForceGasInvariant` previously measured wrapped bank operations under a replacement gas meter with zero-cost KV gas configs, then charged the original transaction meter from that reduced measurement. The fix removes the zero-cost measurement context and tests now require non-zero gas and expect higher gas consumption. This supports security hardening for resource-control/accounting, but not a proven concrete exploit or liveness failure.

## Security Evidence

1. Commit subject says the gas invariant wrapper is fixed to actually charge gas.
2. Implementation removes `WithKVGasConfig(zeroCostGasConfig)` and `WithTransientKVGasConfig(zeroCostGasConfig)` from the measurement context.
3. Measured gas is later applied back to the original transaction gas meter, so suppressed measurement could undercharge the transaction.
4. Tests add `NotZerof(gasConsumed)` for invariant scenarios.
5. Ante test expected gas increases from `38175` to `67193`, supporting that more gas is now charged.

## Missing Evidence

1. No concrete exploit transaction or attacker workflow is shown.
2. No evidence proves chain halt, consensus failure, RPC abuse, or remote denial of service.
3. No authorization bypass, balance theft, signature bypass, or malformed-input crash is supported.
4. No evidence establishes the undercharge magnitude under adversarial workloads beyond the shown test increase.

## Claim Boundaries

1. Keep the finding scoped to gas/resource accounting hardening in bank/EVM transaction processing.
2. Do not claim a confirmed liveness failure from the supplied patch alone.
3. Do not claim RPC exposure; the changed evidence is in transaction/bank gas accounting paths.
4. Do not claim direct financial loss or consensus divergence without additional evidence.
