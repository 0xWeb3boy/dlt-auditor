---
case_id: case_20251024_7c638e51
project: thor
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: core-logic
impact_type:
  - correctness-or-hardening
confidence: medium
source_quality: medium
date: 2025-10-24
source_refs:
  - git:7c638e515cae99ce19fcf353318a764cdef9c798
  - "builtin/staker_native.go:291"
  - "builtin/staker_native.go:245"
  - "builtin/staker/housekeep.go:311"
  - "builtin/staker_native.go:316"
bug_class: unchecked-numeric-conversion
tags:
  - validator-ops
  - core-logic
  - staker
  - integer-overflow
  - input-validation
  - numeric-conversion
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes an unchecked integer conversion issue in builtin staker paths. Native stake increase, stake decrease, and delegation creation now check `staker.ToVET(...)` errors before calling state-changing staker methods, and `ContractBalanceCheck` now checks `ToVET(balance)` before continuing balance reconciliation. The evidence supports an overflow-validation fix, but not stronger claims such as fund theft, validator takeover, or consensus divergence.

## Observed Patch Facts

1. In `builtin/staker_native.go`, the patch replaces `err := Staker.NativeMetered(env.State(), charger).` with `stake, err := staker.ToVET(args.Amount) // convert from wei to VET`.

2. In `builtin/staker_native.go`, the patch replaces `err := Staker.NativeMetered(env.State(), charger).` with `stake, err := staker.ToVET(args.Amount) // convert from wei to VET`.

3. In `builtin/staker/housekeep.go`, the patch replaces `balanceVET := ToVET(balance)` with `balanceVET, err := ToVET(balance)`.

4. In `builtin/staker_native.go`, the patch replaces `AddDelegation(` with `stake, err := staker.ToVET(args.Stake) // convert from wei to VET,`.

## Project Context

The changed code sits primarily in `builtin/staker`, which anchors the finding in the `core-logic` area of the project. Historical context from `builtin/staker_native_gas_test.go`, `builtin/staker/staker.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `builtin/staker/staker.go`, `builtin/staker/transition.go`. The strongest project-level identifiers around this patch are `args`, `staker`, `charger`, and `ToVET`.

## Before/After Behavior

Before the patch, native staker entrypoints passed `staker.ToVET(args.Amount)` or `staker.ToVET(args.Stake)` directly into `IncreaseStake`, `DecreaseStake`, and `AddDelegation`, without an explicit conversion error check at those call sites. `ContractBalanceCheck` similarly assigned `balanceVET := ToVET(balance)` without checking an error. After the patch, these conversions are assigned to local variables with an `err` result; native entrypoints revert on conversion failure, and housekeeping returns the error before continuing.

# Root Cause

Staker amount and balance paths converted big integer values into VET accounting units without checking whether the conversion failed. The supplied evidence indicates this could allow staking/accounting logic to continue after an unsafe or overflowing conversion, but it does not show the exact pre-patch `ToVET` implementation or the concrete resulting corrupted value.

## Walkthrough

1. A native staker call parses an externally supplied `Amount` or `Stake` argument.

2. Before the fix, the entrypoint invoked `staker.ToVET(...)` inline as an argument to a metered state-changing staker method.

3. Because the call site did not inspect a conversion error, the downstream staking operation could be reached even when conversion should have failed.

4. The balance-check path also converted the staker contract balance to VET units without checking a returned error before continuing reconciliation.

5. After the fix, each conversion is performed first and its error is checked immediately.

6. On conversion failure, native calls return a revert and `ContractBalanceCheck` returns the error instead of continuing.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| builtin/staker_native.go | 245 | native IncreaseStake entrypoint validates args.Amount conversion before mutating stake state |
| builtin/staker_native.go | 291 | native DecreaseStake entrypoint validates args.Amount conversion before mutating stake state |
| builtin/staker_native.go | 316 | native AddDelegation entrypoint validates args.Stake conversion before creating delegation state |
| builtin/staker/housekeep.go | 311 | contract balance check validates account balance conversion before comparing tracked staking totals |

## Code Snippets

## Snippet 1

Context: `builtin/staker_native.go:291` (changes persisted or aggregate state handling)

Before
```go
charger := gascharger.New(env)

			err := Staker.NativeMetered(env.State(), charger).
				DecreaseStake(
					thor.Address(args.Validator),
					thor.Address(args.Endorser),
					staker.ToVET(args.Amount), // convert from wei to VET,
				)
```
After
```go
charger := gascharger.New(env)

			stake, err := staker.ToVET(args.Amount) // convert from wei to VET
			if err != nil {
				return nil, staker.NewReverts(err.Error())
			}

			err = Staker.NativeMetered(env.State(), charger).
```

## Snippet 2

Context: `builtin/staker_native.go:245` (changes persisted or aggregate state handling)

Before
```go
charger := gascharger.New(env)

			err := Staker.NativeMetered(env.State(), charger).
				IncreaseStake(
					thor.Address(args.Validator),
					thor.Address(args.Endorser),
					staker.ToVET(args.Amount), // convert from wei to VET
				)
```
After
```go
charger := gascharger.New(env)

			stake, err := staker.ToVET(args.Amount) // convert from wei to VET
			if err != nil {
				return nil, staker.NewReverts(err.Error())
			}

			err = Staker.NativeMetered(env.State(), charger).
```

## Snippet 3

Context: `builtin/staker/housekeep.go:311` (changes persisted or aggregate state handling)

Before
```go
return err
	}
	balanceVET := ToVET(balance)

	// Get the Effective VET tracked
```
After
```go
return err
	}
	balanceVET, err := ToVET(balance)
	if err != nil {
		return err
	}

	// Get the Effective VET tracked
```

## Snippet 4

Context: `builtin/staker_native.go:316` (changes a sensitive control or state-update path)

Before
```go
charger := gascharger.New(env)

			delegationID, err := Staker.NativeMetered(env.State(), charger).
				AddDelegation(
					thor.Address(args.Validator),
					staker.ToVET(args.Stake), // convert from wei to VET,
					args.Multiplier,
					env.BlockContext().Number,
```
After
```go
charger := gascharger.New(env)

			stake, err := staker.ToVET(args.Stake) // convert from wei to VET,
			if err != nil {
				return nil, staker.NewReverts(err.Error())
			}

			delegationID, err := Staker.NativeMetered(env.State(), charger).
```

# Fix Pattern

Perform error-returning numeric conversion before entering staking state logic, check the error immediately, and only pass the validated converted value downstream.

## How It Was Fixed

`builtin/staker_native.go` now validates `staker.ToVET(args.Amount)` before `IncreaseStake` and `DecreaseStake`, and validates `staker.ToVET(args.Stake)` before `AddDelegation`; conversion failures return `staker.NewReverts(err.Error())`. `builtin/staker/housekeep.go` now captures `balanceVET, err := ToVET(balance)` and returns the error if conversion fails.

# Why It Matters

1. Prevents staker accounting from proceeding after a failed amount conversion.

2. Covers stake increase, stake decrease, delegation creation, and contract balance reconciliation paths.

3. The security impact is limited to overflow/unsafe conversion prevention based on the supplied evidence.

4. No supplied evidence proves theft, validator takeover, or consensus divergence.

# Evidence Notes

Grounded evidence is limited to the shown hunks in `builtin/staker_native.go` and `builtin/staker/housekeep.go`, plus the commit subject `Fix overflow issue, add tests (#1456)`. The patch clearly adds error checks around `ToVET` conversions in staker paths. The exact pre-patch overflow mechanics and exploitability are not shown, so confidence is downgraded from high to medium and the verdict remains likely rather than confirmed. Protocol security invariant: Staker accounting should only operate on wei-to-VET converted values after confirming the converted amount is safely representable; failed conversions must stop the staking operation or balance check before state/accounting logic continues. Verification notes: The patch does not show the exact pre-patch ToVET overflow behavior beyond unchecked conversion use. The evidence does not prove a remotely exploitable attack path. The evidence does not prove validator-set takeover, fund theft, or consensus divergence. The generated Solidity/runtime changes are present but not detailed enough here to map additional behavior. Confirmed by diff evidence: conversion errors are now checked before downstream staker operations. Confirmed by diff evidence: housekeeping now returns `ToVET(balance)` errors. Not established: concrete exploit path, attacker capabilities, or impact beyond unsafe conversion handling. Not established: behavior of generated Solidity/runtime artifacts beyond their presence in the commit. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unchecked-numeric-conversion`
Final tags: `validator-ops, core-logic, staker, integer-overflow, input-validation, numeric-conversion`

The supplied patch evidence supports retaining this as security hardening, not a fully proven security fix. The commit explicitly names an overflow issue, and the code now checks `ToVET` conversion errors before state-changing staking and delegation operations and before balance reconciliation. However, the evidence does not show the exact overflow behavior, attacker-controlled exploitability, or concrete security impact, so `security-fix` is too strong.

## Security Evidence

1. Commit subject says "Fix overflow issue".
2. Externally parsed stake amount arguments are converted with `staker.ToVET` before native staking operations.
3. The patch adds error checks that revert before `IncreaseStake`, `DecreaseStake`, and `AddDelegation` proceed.
4. `ContractBalanceCheck` now returns on `ToVET(balance)` conversion failure before continuing reconciliation.
5. Changed paths are in validator/staker accounting logic, a security-sensitive blockchain subsystem.

## Missing Evidence

1. No supplied code shows the implementation or failure semantics of `ToVET`.
2. No concrete exploit path or attacker capability is demonstrated.
3. No evidence proves fund theft, validator takeover, slashing impact, or consensus divergence.
4. Generated Solidity/runtime changes are listed but not explained in the evidence.

## Claim Boundaries

1. Supported claim: unchecked VET conversion errors in staker paths were hardened with explicit checks.
2. Supported claim: the affected code is validator/staker state and accounting logic.
3. Unsupported claim: this definitely fixed an exploitable vulnerability.
4. Unsupported claim: this caused direct financial loss, validator compromise, or consensus failure.
