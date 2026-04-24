---
case_id: case_20220601_37c04d56b5
project: go-ethereum
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: transaction-processing
bug_class: hardening-or-correctness-fix
impact_type:
  - correctness-or-hardening
confidence: medium
source_quality: high
tags:
  - validator-ops
  - transaction-processing
  - hardening-or-correctness-fix
  - correctness-or-hardening
  - validator
date: 2022-06-01
source_refs:
  - git:37c04d56b5db76ad4e0ac9c46e20cf80ca4a7c60
  - "validator/staker.go:367"
  - "validator/staker.go:328"
  - "validator/staker.go:155"
  - "validator/staker.go:80"
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best treated as likely security hardening in the rollup validator withdrawal path. The visible Go changes remove configurable withdrawal destinations from the staker and call `WithdrawStakerFunds` without a destination argument, while the commit subject says validation now enforces contract destination address instead of function signature. The evidence does not prove a concrete exploit or fund theft path.

## Observed Patch Facts

1. In `validator/staker.go`, the patch replaces `if withdrawable.Sign() > 0 && s.withdrawDestination != (common.Address{}) {` with `if withdrawable.Sign() > 0 {`.

2. In `validator/staker.go`, the patch replaces `_, err = s.rollup.WithdrawStakerFunds(s.builder.Auth(ctx), s.withdrawDestination)` with `_, err = s.rollup.WithdrawStakerFunds(s.builder.Auth(ctx))`.

3. In `validator/staker.go`, the patch removes `withdrawDestination := wallet.From()`.

4. In `validator/staker.go`, the patch removes `f.String(prefix+".withdraw-destination", DefaultL1ValidatorConfig.WithdrawDestination...`.

## Project Context

Historical context from `validator/rollup_watcher.go`, `validator/builder_backend.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `validator/validator_wallet.go`, `validator/l1_validator.go`. The strongest project-level identifiers around this patch are `withdrawDestination`, `prefix`, `rollup`, and `WithdrawStakerFunds`.

## Before/After Behavior

Before the patch, the validator staker exposed a `withdraw-destination` config option, derived `withdrawDestination` during staker construction, and passed that address into `WithdrawStakerFunds` in visible withdrawal paths. One path also skipped withdrawal unless the configured destination was nonzero. After the patch, the config option and local destination derivation are removed, both visible calls invoke `WithdrawStakerFunds` without a destination parameter, and the positive-withdrawable-funds path no longer checks a local destination address.

# Root Cause

The apparent issue was that the withdrawal flow carried destination selection or validation through the validator client path. Based on the commit subject, the intended correction was to validate the contract destination address rather than relying on function signature validation. The provided evidence does not include the Solidity diff needed to establish the exact faulty check or exploitability.

## Walkthrough

1. The validator config previously registered a `withdraw-destination` option.

2. `NewStaker` previously derived `withdrawDestination` from the validator wallet address or `config.WithdrawDestination`.

3. An unwanted old deposit path previously called `WithdrawStakerFunds` with `s.withdrawDestination`.

4. The positive withdrawable funds path previously required both positive funds and a nonzero local destination before calling `WithdrawStakerFunds` with that destination.

5. After the patch, both visible calls omit the destination argument, and the local destination config/derivation is removed.

6. The commit subject and changed contract file list support a contract-side destination-validation interpretation, but the actual contract changes are not shown.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| validator/staker.go | 328 | withdraws staker funds after returning an unwanted old deposit; destination argument removed |
| validator/staker.go | 367 | withdraws available validator funds; zero-address destination guard and destination argument removed |
| validator/staker.go | 155 | staker construction no longer derives a configurable withdraw destination from wallet/config |
| validator/staker.go | 80 | validator CLI/config no longer exposes withdraw-destination option |
| contracts/src/rollup/ValidatorWallet.sol | 1 | listed contract-side validator wallet validation logic likely enforcing destination invariant |
| contracts/src/rollup/RollupUserLogic.sol | 1 | listed rollup withdrawal/user logic affected by changed withdrawal interface |

## Code Snippets

## Snippet 1

Context: `validator/staker.go:367` (changes an authorization or privilege gate)

Before
```go
return nil, err
		}
		if withdrawable.Sign() > 0 && s.withdrawDestination != (common.Address{}) {
			_, err = s.rollup.WithdrawStakerFunds(s.builder.Auth(ctx), s.withdrawDestination)
			if err != nil {
				return nil, err
```
After
```go
return nil, err
		}
		if withdrawable.Sign() > 0 {
			_, err = s.rollup.WithdrawStakerFunds(s.builder.Auth(ctx))
			if err != nil {
				return nil, err
```

## Snippet 2

Context: `validator/staker.go:328` (changes an authorization or privilege gate)

Before
```go
}
			if stakeIsUnwanted {
				_, err = s.rollup.WithdrawStakerFunds(s.builder.Auth(ctx), s.withdrawDestination)
				if err != nil {
					return nil, err
```
After
```go
}
			if stakeIsUnwanted {
				_, err = s.rollup.WithdrawStakerFunds(s.builder.Auth(ctx))
				if err != nil {
					return nil, err
```

## Snippet 3

Context: `validator/staker.go:155` (changes a sensitive control or state-update path)

Before
```go
return nil, err
	}
	withdrawDestination := wallet.From()
	if common.IsHexAddress(config.WithdrawDestination) {
		withdrawDestination = common.HexToAddress(config.WithdrawDestination)
	}
	return &Staker{
		L1Validator:         val,
```
After
```go
return nil, err
	}
	return &Staker{
		L1Validator:         val,
```

## Snippet 4

Context: `validator/staker.go:80` (changes a consensus- or validator-sensitive branch)

Before
```go
L1PostingStrategyAddOptions(prefix+".posting-strategy", f)
	f.Bool(prefix+".disable-challenge", DefaultL1ValidatorConfig.DisableChallenge, "disable validator challenge")
	f.String(prefix+".withdraw-destination", DefaultL1ValidatorConfig.WithdrawDestination, "validator withdraw destination")
	f.Int(prefix+".target-machine-count", DefaultL1ValidatorConfig.TargetMachineCount, "target machine count")
	f.Int64(prefix+".confirmation-blocks", DefaultL1ValidatorConfig.ConfirmationBlocks, "confirmation blocks")
```
After
```go
L1PostingStrategyAddOptions(prefix+".posting-strategy", f)
	f.Bool(prefix+".disable-challenge", DefaultL1ValidatorConfig.DisableChallenge, "disable validator challenge")
	f.Int(prefix+".target-machine-count", DefaultL1ValidatorConfig.TargetMachineCount, "target machine count")
	f.Int64(prefix+".confirmation-blocks", DefaultL1ValidatorConfig.ConfirmationBlocks, "confirmation blocks")
```

# Fix Pattern

Remove caller-configured destination selection from the validator staker path and shift the relevant destination invariant to the contract-facing withdrawal interface.

## How It Was Fixed

The Go validator staker no longer accepts, derives, stores, or passes a withdrawal destination. `WithdrawStakerFunds` is called without a destination argument in the visible withdrawal paths, and the CLI/config option for `withdraw-destination` is removed. Contract files are listed as changed, but their concrete changes are not provided.

# Why It Matters

1. A validator withdrawal destination is security-sensitive.

2. Removing local destination configuration reduces one source of misrouting or validation confusion.

3. The commit subject indicates a stronger destination-based validation invariant.

4. No concrete attacker path is proven from the supplied hunks alone.

# Evidence Notes

Grounded evidence comes from `validator/staker.go` hunks at the config option, constructor, and two withdrawal call sites. The commit subject explicitly references enforcing contract destination address instead of function signature. The file list includes `ValidatorWallet.sol` and `RollupUserLogic.sol`, but their diffs are absent, so claims about exact Solidity behavior, attacker-controlled calldata, or theft must be avoided. Protocol security invariant: Validator wallet and staker withdrawal flows should validate the intended contract destination address for rollup wallet calls, rather than depending on a function signature check or a locally configured withdrawal destination in the validator client. Verification notes: The patch evidence does not prove funds could be stolen before the change. The exact pre-patch contract validation logic is not shown in the provided hunks. No concrete attacker-controlled calldata or arbitrary destination exploit path is demonstrated. The visible Go changes alone could also be API simplification; the security interpretation depends on the commit subject and listed contract files. No Solidity diff was provided for direct validation of the contract-side invariant. No regression test contents were provided. Exploitability is not established by the visible Go changes alone. Classification is likely security hardening, not a confirmed vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`

The supplied evidence supports retaining this as security hardening, but not as a confirmed vulnerability fix. The visible Go changes remove a configurable withdrawal destination from validator staker behavior and update withdrawal calls to no longer pass caller-selected destination data. Combined with the commit subject stating validation now enforces the contract destination address instead of a function signature, this plausibly tightens a security-sensitive withdrawal/validator-wallet invariant. The evidence does not prove an exploitable fund theft or bypass path because the key contract-side diff is not shown.

## Security Evidence

1. Commit subject explicitly describes changing validation from function signature to contract destination address enforcement.
2. Validator staker withdrawal calls no longer pass a locally configured withdrawDestination argument.
3. The validator CLI/config option for withdraw-destination is removed.
4. Changed file list includes ValidatorWallet.sol, RollupUserLogic.sol, rollup interfaces, and validator-wallet tests, indicating the withdrawal validation interface changed across contract and client code.

## Missing Evidence

1. No Solidity diff is provided showing the actual destination-address validation logic.
2. No regression test contents are provided to demonstrate the rejected unsafe case.
3. No concrete attacker-controlled calldata, arbitrary destination, or fund theft path is shown.
4. The visible Go hunks alone could also be explained as API cleanup around withdrawal routing.

## Claim Boundaries

1. Treat as security-hardening, not a proven security-fix.
2. Do not claim confirmed exploitability or stolen funds from the supplied evidence.
3. Do not describe the exact faulty contract check beyond the commit subject's function-signature versus destination-address wording.
4. Keep claims focused on withdrawal destination validation and removal of caller-configured destination selection.
