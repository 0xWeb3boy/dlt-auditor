---
case_id: case_20230614_24bcee3d95
project: avalanchego
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
bug_class: access-control
confidence: medium
source_quality: high
date: 2023-06-14
source_refs:
  - git:24bcee3d957546fed520a85bb43996ffbe502c38
  - "vms/platformvm/txs/executor/staker_tx_verification.go:1225"
  - "vms/platformvm/state/staker.go:207"
  - "vms/platformvm/txs/executor/staker_tx_verification.go:1121"
  - "vms/platformvm/txs/executor/staker_tx_verification.go:1126"
impact_type:
  - unauthorized-staker-stop
tags:
  - validator-ops
  - staking
  - authorization
  - continuous-staking
  - management-key
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes an authorization error in PlatformVM continuous staking stop handling. The strongest evidence is that StopStakerTx authorization changed from deriving an owner from reward-owner or subnet-owner fields to requiring the referenced staking transaction to implement txs.ContinuousStaker and verifying permission against its ManagementKey().

## Observed Patch Facts

1. In `vms/platformvm/txs/executor/staker_tx_verification.go`, the patch replaces `var stakerOwner fx.Owner` with `continuousStakerTx, ok := stakerTx.Unsigned.(txs.ContinuousStaker)`.

2. In `vms/platformvm/state/staker.go`, the patch replaces `func (s *Staker) EarliestStopTime() time.Time {` with `func MarkStakerForRemovalInPlaceBeforeTime(s *Staker, stopTime time.Time) {`.

3. In `vms/platformvm/txs/executor/staker_tx_verification.go`, the patch removes `if !backend.Config.IsContinuousStakingActivated(chainState.GetTimestamp()) {`.

4. In `vms/platformvm/txs/executor/staker_tx_verification.go`, the patch replaces `var (` with `currentTimestamp := chainState.GetTimestamp()`.

## Project Context

The changed code sits primarily in `vms/platformvm/txs/executor`, `vms/platformvm/txs`, `vms/platformvm/state`, which anchors the finding in the `staking` area of the project. Historical context from `vms/platformvm/txs/executor/advance_time_test.go`, `vms/platformvm/txs/executor/backend.go` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `vms/platformvm/txs/executor/proposal_tx_executor.go`, `vms/platformvm/txs/executor/tx_mempool_verifier.go`. The strongest project-level identifiers around this patch are `time`, `Time`, `uStakerTx`, and `backend`. Nearby tests or test-like files include `vms/platformvm/vm_regression_test.go`.

## Before/After Behavior

Before the patch, verifyStopStakerAuthorization loaded the referenced staker transaction and selected an authorization owner based on the unsigned transaction shape, including validator reward owner, delegator reward owner, or subnet ownership logic. After the patch, it rejects referenced transactions that are not txs.ContinuousStaker and authorizes against continuousStakerTx.ManagementKey(). The fork activation check remains in verifyStopStakerTx after syntactic verification. The staker timing change replaces EarliestStopTime with MarkStakerForRemovalInPlaceBeforeTime, which only shortens EndTime when the requested stop time precedes the current EndTime and aligns the new end time to staking periods.

# Root Cause

The prior StopStakerTx authorization path was tied to ownership fields derived from the target transaction type rather than the management key associated with a continuous staker. Based on the patch, that was not the intended authority for stopping continuous stakers.

## Walkthrough

1. verifyStopStakerTx syntactically verifies the signed StopStakerTx.

2. The verification path checks the chain timestamp and rejects the transaction if continuous staking is not active.

3. verifyStopStakerAuthorization loads the referenced staker transaction from chain state.

4. Before the patch, the authorization owner was selected from validator, delegator, or subnet-related owner fields.

5. After the patch, the referenced transaction must implement txs.ContinuousStaker.

6. If the referenced transaction is not a continuous staker, authorization fails with ErrUnauthorizedStakerStopping.

7. If it is a continuous staker, permission is verified against continuousStakerTx.ManagementKey().

8. The related state helper updates EndTime only within the stop/removal timing rules.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| vms/platformvm/txs/executor/staker_tx_verification.go | 1203 | verifies StopStakerTx authorization against the referenced continuous staker management key |
| vms/platformvm/txs/executor/staker_tx_verification.go | 1117 | validates StopStakerTx syntactic form and continuous-staking fork activation before retrieving and stopping the staker |
| vms/platformvm/state/staker.go | 205 | updates staker end time for removal before a requested stop time while preserving period alignment |

## Code Snippets

## Snippet 1

Context: `vms/platformvm/txs/executor/staker_tx_verification.go:1225` (changes an authorization or privilege gate)

Before
```go
}

	var stakerOwner fx.Owner
	switch uStakerTx := stakerTx.Unsigned.(type) {
	case txs.ValidatorTx:
		stakerOwner = uStakerTx.ValidationRewardsOwner()
	case txs.DelegatorTx:
		stakerOwner = uStakerTx.RewardsOwner()
```
After
```go
}

	continuousStakerTx, ok := stakerTx.Unsigned.(txs.ContinuousStaker)
	if !ok {
		return nil, ErrUnauthorizedStakerStopping
	}

	err = backend.Fx.VerifyPermission(sTx.Unsigned, stakerAuth, stakerCred, continuousStakerTx.ManagementKey())
```

## Snippet 2

Context: `vms/platformvm/state/staker.go:207` (changes a sensitive control or state-update path)

Before
```go
}

func (s *Staker) EarliestStopTime() time.Time {
	candidateStopTime := s.NextTime
	if s.Priority.IsValidator() && s.SubnetID == constants.PrimaryNetworkID {
		candidateStopTime = s.NextTime.Add(s.StakingPeriod) // stop at T+1 for now
	}
	if candidateStopTime.Before(s.EndTime) {
```
After
```go
}

func MarkStakerForRemovalInPlaceBeforeTime(s *Staker, stopTime time.Time) {
	if !stopTime.Before(s.EndTime) {
		return
	}

	end := s.NextTime
```

## Snippet 3

Context: `vms/platformvm/txs/executor/staker_tx_verification.go:1121` (changes a consensus- or validator-sensitive branch)

Before
```go
tx *txs.StopStakerTx,
) ([]*state.Staker, time.Time, error) {
	if !backend.Config.IsContinuousStakingActivated(chainState.GetTimestamp()) {
		return nil, time.Time{}, errors.New("StopStakerTx cannot be accepted before continuous staking fork activation")
	}

	// Verify the tx is well-formed
	if err := sTx.SyntacticVerify(backend.Ctx); err != nil {
```
After
```go
tx *txs.StopStakerTx,
) ([]*state.Staker, time.Time, error) {
	// Verify the tx is well-formed
	if err := sTx.SyntacticVerify(backend.Ctx); err != nil {
```

## Snippet 4

Context: `vms/platformvm/txs/executor/staker_tx_verification.go:1126` (changes a sensitive control or state-update path)

Before
```go
}

	// retrieve staker to be stopped
	var (
```
After
```go
}

	currentTimestamp := chainState.GetTimestamp()
	if !backend.Config.IsContinuousStakingActivated(currentTimestamp) {
		return nil, time.Time{}, ErrTxUnacceptableBeforeFork
	}

	// retrieve staker to be stopped
```

# Fix Pattern

Authorize the stop operation against the explicit management authority of the target continuous staker and reject unsupported target transaction types before permission verification.

## How It Was Fixed

verifyStopStakerAuthorization now type-checks the referenced transaction as txs.ContinuousStaker and passes continuousStakerTx.ManagementKey() to backend.Fx.VerifyPermission. Non-continuous targets are rejected. The stop transaction path also retains the continuous-staking activation gate, and the state update logic was adjusted to shorten EndTime only on staking-period boundaries.

# Why It Matters

1. Stopping a staker is a state-changing staking operation.

2. Reward owners or subnet owners are not necessarily the same authority as a continuous staker management key.

3. The patch establishes an explicit target-type and management-key authorization check.

4. The evidence supports an authorization fix, but not direct theft, key compromise, or live exploitability.

# Evidence Notes

The security-relevant evidence is concentrated in vms/platformvm/txs/executor/staker_tx_verification.go, where StopStakerTx authorization changes to require txs.ContinuousStaker and ManagementKey(). The state/staker.go timing change supports the same stop/removal workflow but is not independently established as a vulnerability. The provided evidence does not prove a specific attacker, live-network exploitability, asset theft, or consensus takeover. Protocol security invariant: A StopStakerTx for continuous staking should only target a transaction that is actually a continuous staker and should be authorized by that staker transaction's management key. Verification notes: The patch does not prove that an unauthorized stop was exploitable on a live network. The patch does not show a direct theft, key compromise, or consensus takeover primitive. The exact unauthorized actor under the old reward-owner/subnet-owner authorization model is not fully proven from the provided context. The state timing change is security-adjacent business logic, but not independently proven to be a vulnerability. Supported by direct before/after authorization changes in verifyStopStakerAuthorization. Supported by retained fork activation check in verifyStopStakerTx. State timing changes should be treated as supporting business logic, not the root security issue. Confidence remains medium because exploitability and the exact unauthorized actor are not shown in the provided input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final impact type: `unauthorized-staker-stop`
Final tags: `validator-ops, staking, authorization, continuous-staking, management-key`

The supplied patch clearly changes StopStakerTx authorization from deriving authority from reward/subnet owner fields to requiring the referenced transaction to be a ContinuousStaker and verifying against its ManagementKey. That is security-sensitive authorization tightening in validator staking logic, but the evidence does not prove a concrete exploitable unauthorized-stop scenario or live impact strongly enough to retain it as a definite security-fix rather than hardening.

## Security Evidence

1. verifyStopStakerAuthorization now rejects target transactions that do not implement txs.ContinuousStaker.
2. Permission verification now uses continuousStakerTx.ManagementKey() instead of owner fields derived from validator, delegator, or subnet transaction types.
3. The changed path governs StopStakerTx handling, a state-changing staking operation.
4. The fork activation guard remains present after syntactic verification, preserving an acceptance gate for StopStakerTx.

## Missing Evidence

1. No explicit exploit scenario showing who could stop a staker before the patch.
2. No test excerpt demonstrating an unauthorized reward owner or subnet owner was previously accepted.
3. No commit body or advisory confirming a security vulnerability.
4. The state timing change is not independently shown to be security-relevant.

## Claim Boundaries

1. Supports authorization hardening for continuous staker stop operations.
2. Does not support claims of asset theft, key compromise, or consensus takeover.
3. Does not prove the old owner-selection behavior was exploitable on a live network.
4. Should not be generalized beyond StopStakerTx continuous staking authorization.
