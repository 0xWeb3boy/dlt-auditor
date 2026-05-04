---
case_id: case_20260325_d5d9e64da0
project: avalanchego
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2026-03-25
source_refs:
  - git:d5d9e64da00553284a723e0b2c5c9741e96863bb
  - "vms/platformvm/state/state.go:1925"
  - "vms/platformvm/txs/executor/staker_tx_verification.go:996"
  - "vms/platformvm/state/state_test.go:713"
  - "vms/platformvm/txs/executor/reward_validator_test.go:1370"
bug_class: unchecked-validator-weight-overflow
impact_type:
  - consensus-state-integrity
confidence: medium
tags:
  - staking
  - validator-accounting
  - integer-overflow
  - checked-arithmetic
  - consensus-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a concrete unchecked uint64 addition in PlatformVM auto-renewed validator state loading and improves error propagation for staker transaction lookup. The changed code is consensus-sensitive validator accounting, but the provided evidence does not establish an externally triggerable vulnerability, consensus split, funds loss, or node crash. Treat this as security-relevant robustness with unclear vulnerability status.

## Observed Patch Facts

1. In `vms/platformvm/state/state.go`, the patch replaces `// todo: add tests` with `weight, err := safemath.Add(stakerTx.Weight(), metadata.AccruedRewards)`.

2. In `vms/platformvm/txs/executor/staker_tx_verification.go`, the patch adds `if errors.Is(err, database.ErrNotFound) {`.

3. In `vms/platformvm/state/state_test.go`, the patch replaces `func TestValidatorWeightDiff(t *testing.T) {` with `func createAutoRenewedValidatorTx(t testing.TB, nodeID ids.NodeID, weight uint64, per...`.

4. In `vms/platformvm/txs/executor/reward_validator_test.go`, the patch adds `// TestRewardDelegatorToAutoRenewedValidator tests the full delegator reward`.

## Project Context

The changed code sits primarily in `vms/platformvm/state`, `vms/platformvm`, `vms/platformvm/txs/executor`, which anchors the finding in the `staking` area of the project. Historical context from `vms/platformvm/state/metadata_delegator_test.go`, `vms/platformvm/state/metadata_delegator.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vms/platformvm/txs/executor/standard_tx_executor_test.go`, `vms/platformvm/txs/executor/standard_tx_executor.go`. The strongest project-level identifiers around this patch are `weight`, `stakerTx`, `metadata`, and `delegator`. Nearby tests or test-like files include `vms/platformvm/vm_regression_test.go`, `vms/platformvm/txs/txstest/context.go`.

## Before/After Behavior

Before the patch, `State.loadCurrentValidators` computed auto-renewed validator weight using unchecked `stakerTx.Weight() + metadata.AccruedRewards + metadata.AccruedDelegateeRewards`, which could wrap on uint64 overflow. After the patch, the additions use `safemath.Add` and return `overflow computing weight` on overflow. Separately, `verifySetAutoRenewedValidatorConfigTx` now maps only `database.ErrNotFound` to `ErrMissingStakerTx` and wraps other `GetTx` errors instead of collapsing all lookup failures into the missing-staker case.

# Root Cause

Unchecked uint64 arithmetic was used while reconstructing an auto-renewed validator's effective weight from persisted state. A secondary robustness issue was broad error collapsing during staker transaction lookup.

## Walkthrough

1. `loadCurrentValidators` loads persisted current validator entries and associated metadata.

2. For `AddAutoRenewedValidatorTx`, the old code added base weight, accrued rewards, and accrued delegatee rewards in one unchecked uint64 expression.

3. If the mathematical sum exceeded uint64 capacity, Go arithmetic would wrap silently.

4. The patch replaces the expression with sequential `safemath.Add` calls.

5. Each overflow path now returns an explicit error instead of constructing a staker with wrapped weight.

6. `verifySetAutoRenewedValidatorConfigTx` now distinguishes `database.ErrNotFound` from other database or state lookup errors.

7. Added tests support auto-renewed validator construction, weight behavior, and delegator reward flow.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vms/platformvm/state/state.go | 1925 | loads current validators and computes AddAutoRenewedValidatorTx effective weight from base weight plus accrued rewards |
| vms/platformvm/txs/executor/staker_tx_verification.go | 996 | verifies SetAutoRenewedValidatorConfigTx and reports missing staker tx separately from other state/database failures |
| vms/platformvm/state/state_test.go | 713 | adds test helper coverage for auto-renewed validator transactions and weight cases |
| vms/platformvm/txs/executor/reward_validator_test.go | 1370 | adds reward-flow coverage for delegator rewards deferred to auto-renewed validator delegatee reward state |

## Code Snippets

## Snippet 1

Context: `vms/platformvm/state/state.go:1925` (changes a sensitive control or state-update path)

Before
```go
}

		// todo: add tests
		var staker *Staker
		switch stakerTx := tx.Unsigned.(type) {
		case *txs.AddAutoRenewedValidatorTx:
			weight := stakerTx.Weight() + metadata.AccruedRewards + metadata.AccruedDelegateeRewards
```
After
```go
}

		var staker *Staker
		switch stakerTx := tx.Unsigned.(type) {
		case *txs.AddAutoRenewedValidatorTx:
			weight, err := safemath.Add(stakerTx.Weight(), metadata.AccruedRewards)
			if err != nil {
				return fmt.Errorf("overflow computing weight: %w", err)
```

## Snippet 2

Context: `vms/platformvm/txs/executor/staker_tx_verification.go:996` (changes persisted or aggregate state handling)

Before
```go
stakerTx, _, err := chainState.GetTx(tx.TxID)
	if err != nil {
		return nil, ErrMissingStakerTx
	}
```
After
```go
stakerTx, _, err := chainState.GetTx(tx.TxID)
	if err != nil {
		if errors.Is(err, database.ErrNotFound) {
			return nil, ErrMissingStakerTx
		}

		return nil, fmt.Errorf("error getting staker tx: %w", err)
	}
```

## Snippet 3

Context: `vms/platformvm/state/state_test.go:713` (changes an authorization or privilege gate)

Before
```go
}

func TestValidatorWeightDiff(t *testing.T) {
	type op struct {
```
After
```go
}

func createAutoRenewedValidatorTx(t testing.TB, nodeID ids.NodeID, weight uint64, period uint64) *txs.AddAutoRenewedValidatorTx {
	sk, err := localsigner.New()
	require.NoError(t, err)
	sig, err := signer.NewProofOfPossession(sk)
	require.NoError(t, err)
```

## Snippet 4

Context: `vms/platformvm/txs/executor/reward_validator_test.go:1370` (changes an authorization or privilege gate)

Before
```go
}
}
```
After
```go
}
}

// TestRewardDelegatorToAutoRenewedValidator tests the full delegator reward
// flow for a delegator to an auto-renewed validator: delegator gets their
// share, delegatee share is deferred to StakingInfo.DelegateeReward.
func TestRewardDelegatorToAutoRenewedValidator(t *testing.T) {
	var (
```

# Fix Pattern

Replace unchecked consensus-sensitive arithmetic with checked math and return ordinary errors on overflow; preserve specific state lookup error semantics instead of flattening unrelated errors.

## How It Was Fixed

`vms/platformvm/state/state.go` now computes auto-renewed validator weight through two checked `safemath.Add` calls. `vms/platformvm/txs/executor/staker_tx_verification.go` now returns `ErrMissingStakerTx` only for `database.ErrNotFound` and wraps other lookup errors with context. Supporting tests were added around auto-renewed validator setup and reward behavior.

# Why It Matters

1. Validator weight accounting is consensus-sensitive.

2. Unchecked uint64 overflow can silently produce an incorrect represented weight.

3. The evidence shows a real overflow fix, but not a proven exploit path.

4. The lookup change improves diagnosability and error handling, not access control.

# Evidence Notes

Strong evidence supports the uint64 overflow fix in `vms/platformvm/state/state.go` and the error-handling change in `vms/platformvm/txs/executor/staker_tx_verification.go`. The test additions are supporting evidence only. The provided material does not show that an attacker can create overflowing persisted metadata or rewards, nor does it demonstrate concrete security impact. Protocol security invariant: Auto-renewed validator effective weight should be reconstructed from base weight and accrued rewards without uint64 wraparound; if the sum cannot be represented, state loading should return an error rather than install a wrapped weight. Verification notes: No proof is shown that an attacker can force persisted metadata or rewards into an overflowing state. No concrete consensus split, funds loss, or node crash is demonstrated by the patch evidence alone. The error-handling change does not by itself show an access-control fix. Test additions support the fix but are not independent evidence of exploitability. No external exploitability is established by the provided evidence. No concrete consensus split, funds loss, or node crash is demonstrated. Helper and test additions should not be treated as root cause. Access-control claims are unsupported by the shown diff. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unchecked-validator-weight-overflow`
Final impact type: `consensus-state-integrity`
Final confidence: `medium`
Final tags: `staking, validator-accounting, integer-overflow, checked-arithmetic, consensus-hardening`

The patch clearly replaces unchecked uint64 arithmetic in auto-renewed validator weight reconstruction with checked safemath and explicit overflow errors. Because this occurs while loading current validators and computing consensus-sensitive staking weight, it removes a risky condition in validator accounting. The evidence does not prove attacker control, exploitability, funds loss, crash, or a concrete consensus split, so this should be retained as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. Unchecked addition of validator weight plus accrued rewards was replaced with checked safemath.Add calls.
2. Overflow now returns an explicit error instead of silently wrapping uint64 weight.
3. The changed path loads current validators and reconstructs auto-renewed validator staking weight from persisted metadata.
4. The commit subject specifically identifies an overflow in auto-renewed validator weight.

## Missing Evidence

1. No proof that an external actor can force overflowing accrued reward metadata.
2. No demonstrated consensus split, funds loss, node crash, or denial of service scenario.
3. No invariant or test output showing the pre-patch wrapped weight causing a concrete security failure.
4. The staker transaction lookup change appears to be error-handling robustness, not independently security-relevant.

## Claim Boundaries

1. Classify as security-hardening, not a proven exploitable vulnerability.
2. Do not claim access-control or privilege-check impact from the provided test/helper changes.
3. Do not claim funds loss or consensus failure beyond potential validator-weight integrity risk.
4. Treat tests as supporting evidence only, not independent proof of exploitability.
