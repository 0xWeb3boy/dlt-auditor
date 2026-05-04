---
case_id: case_20260325_fc749bb8c1
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
  - git:fc749bb8c1acfc6fbbb175c52eeb8e9c718d66d3
  - "vms/platformvm/state/state.go:1919"
  - "vms/platformvm/txs/executor/staker_tx_verification.go:996"
  - "vms/platformvm/state/state_test.go:713"
  - "vms/platformvm/txs/executor/reward_validator_test.go:1370"
bug_class: integer-overflow-hardening
impact_type:
  - state-integrity
  - consensus-integrity
confidence: medium
tags:
  - staking
  - validator
  - integer-overflow
  - checked-arithmetic
  - consensus-state
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes unchecked uint64 arithmetic when loading current auto-renewed validators. Before the patch, loadCurrentValidators added stakerTx.Weight(), metadata.AccruedRewards, and metadata.AccruedDelegateeRewards directly, which could wrap if the sum exceeded uint64 capacity. After the patch, the additions use safemath.Add and return an overflow error. This is plausibly security relevant because the code is in validator state reconstruction, but the supplied evidence does not establish attacker control, exploitability, consensus divergence, node crash, or asset loss. Treat as unclear rather than a confirmed security fix.

## Observed Patch Facts

1. In `vms/platformvm/state/state.go`, the patch replaces `// todo: add tests` with `weight, err := safemath.Add(stakerTx.Weight(), metadata.AccruedRewards)`.

2. In `vms/platformvm/txs/executor/staker_tx_verification.go`, the patch adds `if errors.Is(err, database.ErrNotFound) {`.

3. In `vms/platformvm/state/state_test.go`, the patch replaces `func TestValidatorWeightDiff(t *testing.T) {` with `func createAutoRenewedValidatorTx(t testing.TB, nodeID ids.NodeID, weight uint64, per...`.

4. In `vms/platformvm/txs/executor/reward_validator_test.go`, the patch adds `// TestRewardDelegatorToAutoRenewedValidator tests the full delegator reward`.

## Project Context

The changed code sits primarily in `vms/platformvm/state`, `vms/platformvm`, `vms/platformvm/txs/executor`, which anchors the finding in the `staking` area of the project. Historical context from `vms/platformvm/state/metadata_delegator_test.go`, `vms/platformvm/state/metadata_delegator.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vms/platformvm/txs/executor/standard_tx_executor_test.go`, `vms/platformvm/txs/executor/standard_tx_executor.go`. The strongest project-level identifiers around this patch are `weight`, `stakerTx`, `metadata`, and `delegator`. Nearby tests or test-like files include `vms/platformvm/vm_regression_test.go`, `vms/platformvm/txs/txstest/context.go`.

## Before/After Behavior

Before the patch, AddAutoRenewedValidatorTx effective weight was rebuilt with unchecked uint64 addition and would silently wrap on overflow. After the patch, the same calculation is performed with checked safemath.Add calls, and loadCurrentValidators returns fmt.Errorf("overflow computing weight: %w", err) if either addition overflows. A secondary change in verifySetAutoRenewedValidatorConfigTx preserves ErrMissingStakerTx only for database.ErrNotFound and wraps other GetTx errors.

# Root Cause

The grounded root cause is unchecked integer arithmetic in the state-loading path for current auto-renewed validators. The previous code did not enforce that original validator weight plus accrued validator rewards plus accrued delegatee rewards fit in uint64 before using the derived weight.

## Walkthrough

1. State.loadCurrentValidators iterates current validators, loads each validator transaction, and parses validator metadata.

2. For AddAutoRenewedValidatorTx, the pre-fix code directly computed stakerTx.Weight() + metadata.AccruedRewards + metadata.AccruedDelegateeRewards.

3. In Go, uint64 addition wraps on overflow, so an oversized sum would produce a smaller effective weight.

4. The patch replaces the direct expression with two safemath.Add calls and checks the returned error after each addition.

5. If either addition overflows, loadCurrentValidators now returns an ordinary overflow error instead of using a wrapped weight.

6. verifySetAutoRenewedValidatorConfigTx was also changed to distinguish database.ErrNotFound from other GetTx failures.

7. Added tests and helpers support auto-renewed validator construction, weight behavior, and delegator reward accounting, but they do not prove exploitability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vms/platformvm/state/state.go | 1919 | Reconstructs current auto-renewed validator weight from transaction weight and accrued reward metadata; changed from unchecked addition to checked safemath addition. |
| vms/platformvm/txs/executor/staker_tx_verification.go | 996 | Verifies SetAutoRenewedValidatorConfigTx by loading the referenced staker transaction; changed to distinguish missing transactions from other database errors. |
| vms/platformvm/txs/executor/reward_validator_test.go | 1370 | Adds coverage for delegator reward flow to auto-renewed validators, including deferred delegatee reward accounting. |
| vms/platformvm/state/state_test.go | 713 | Adds auto-renewed validator test helper coverage around validator weight/state behavior. |

## Code Snippets

## Snippet 1

Context: `vms/platformvm/state/state.go:1919` (changes a sensitive control or state-update path)

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

Replace unchecked arithmetic in consensus-sensitive state reconstruction with checked arithmetic, and fail with an explicit error when the derived value cannot be represented. Keep storage not-found errors distinct from unexpected storage failures.

## How It Was Fixed

In vms/platformvm/state/state.go, the patch changed AddAutoRenewedValidatorTx weight reconstruction to call safemath.Add for stakerTx.Weight() plus metadata.AccruedRewards, then again for metadata.AccruedDelegateeRewards. Each overflow returns an error. In vms/platformvm/txs/executor/staker_tx_verification.go, GetTx error handling now maps only database.ErrNotFound to ErrMissingStakerTx and wraps other errors.

# Why It Matters

1. Validator weight reconstruction affects PlatformVM staking state.

2. Unchecked uint64 addition can silently install an incorrect wrapped weight.

3. The fix enforces representability of derived auto-renewed validator weight.

4. The evidence does not prove a remotely triggerable exploit or concrete security impact.

5. The GetTx error handling change appears secondary and is not independently security-proven.

# Evidence Notes

Strong evidence supports an unchecked-overflow cleanup in vms/platformvm/state/state.go around loadCurrentValidators. The exact changed expression replaced direct uint64 addition with safemath.Add calls. The code location is consensus-sensitive, but the provided evidence does not show how an attacker can create overflowing persisted metadata, whether such state can arise through valid protocol actions, or whether overflow would cause a security failure rather than a local consistency bug. Claims of denial of service, consensus split, fund theft, or authorization bypass are unsupported. Protocol security invariant: PlatformVM staking state should reconstruct an auto-renewed validator's effective weight from the validator weight plus accrued reward metadata without uint64 wraparound, and should return an ordinary error if the value cannot be represented. Verification notes: The patch does not prove that an attacker can create persisted metadata with overflowing accrued rewards. The patch does not prove a remote node crash, only that overflow is now converted into an error in state loading. The patch does not prove fund theft or authorization bypass. The GetTx error handling change is not enough on its own to establish a security vulnerability. Tests support the intended reward/weight behavior but are not independent proof of exploitability. Confirmed by supplied diff: unchecked uint64 addition was replaced with safemath.Add. Security relevance is plausible because the code reconstructs validator state. Exploitability is not established by the provided evidence. Helper and test additions should be treated as support code, not root cause. Keep out of the security corpus unless additional evidence shows attacker-controlled overflow or concrete protocol impact. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow-hardening`
Final impact type: `state-integrity, consensus-integrity`
Final confidence: `medium`
Final tags: `staking, validator, integer-overflow, checked-arithmetic, consensus-state`

The supplied patch clearly replaces unchecked uint64 addition in auto-renewed validator weight reconstruction with checked safemath additions and explicit overflow errors. Because this calculation affects PlatformVM validator state, the change is security-sensitive hardening. However, the evidence does not prove attacker-controlled overflow, concrete exploitability, consensus divergence, denial of service, or asset loss, so it should not be upgraded to a confirmed security fix.

## Security Evidence

1. Unchecked uint64 addition of validator weight plus accrued rewards was replaced with safemath.Add.
2. The changed calculation is in loadCurrentValidators, a validator state reconstruction path.
3. The commit subject explicitly identifies an overflow in auto-renewed validator weight.
4. Tests were added around auto-renewed validator reward and weight behavior.

## Missing Evidence

1. No evidence that an attacker can cause the overflowing metadata through valid protocol actions.
2. No demonstrated consensus split, node crash, asset loss, or privilege bypass.
3. No evidence that the secondary GetTx error handling change fixes a security issue.
4. No concrete reproduction showing the pre-patch overflow becoming exploitable.

## Claim Boundaries

1. Treat as security hardening, not a confirmed exploitable vulnerability.
2. Do not claim fund theft, authorization bypass, or remote denial of service from the supplied evidence.
3. The supported root cause is unchecked arithmetic in validator weight reconstruction.
4. The GetTx error handling change is reliability/error-preservation evidence only unless separately proven security-relevant.
