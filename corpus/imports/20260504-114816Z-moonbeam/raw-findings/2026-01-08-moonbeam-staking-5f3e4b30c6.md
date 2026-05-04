---
case_id: case_20260108_5f3e4b30c6
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: staking
bug_class: state-corruption
impact_type:
  - state-integrity
confidence: medium
source_quality: high
tags:
  - blockchain-core
  - staking
  - state-corruption
  - state-integrity
  - snapshot
date: 2026-01-08
source_refs:
  - git:5f3e4b30c6683db59b0efc3f17731b445f5a8065
  - "pallets/parachain-staking/src/delegation_requests.rs:222"
  - "pallets/parachain-staking/src/lib.rs:2212"
  - "pallets/parachain-staking/src/tests.rs:364"
  - "pallets/parachain-staking/src/tests.rs:34"
validation_status: completed
security_verdict: likely
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant staking reward accounting bug involving stacked delegation Decrease requests. The supplied evidence supports that multiple pending decreases could previously be validated individually but later aggregated in reward snapshot accounting, allowing uncounted_stake to exceed the real bonded amount and corrupt the payout denominator. The evidence supports a monetary accounting invariant issue, but does not prove exploitability details or quantify loss.

## Observed Patch Facts

1. In `pallets/parachain-staking/src/delegation_requests.rs`, the patch replaces `let new_amount: BalanceOf<T> = (bonded_amount - decrease_amount).into();` with `// Cumulative safety: multiple pending Decrease requests for the same`.

2. In `pallets/parachain-staking/src/lib.rs`, the patch replaces `uncounted_stake = uncounted_stake.saturating_add(*amount);` with `// For revokes, the entire current bond is excluded from rewards.`.

3. In `pallets/parachain-staking/src/tests.rs`, the patch replaces `// ~~ MONETARY GOVERNANCE ~~` with `#[test]`.

4. In `pallets/parachain-staking/src/tests.rs`, the patch replaces `AtStake, Bond, CollatorStatus, DelegationScheduledRequests,` with `AtStake, AwardedPts, Bond, CollatorStatus, DelegationScheduledRequests,`.

## Project Context

The changed code sits primarily in `pallets/parachain-staking/src`, `pallets/parachain-staking`, which anchors the finding in the `staking` area of the project. Historical context from `pallets/parachain-staking/src/benchmarks.rs`, `pallets/parachain-staking/src/types.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `pallets/parachain-staking/src/benchmarks.rs`, `pallets/parachain-staking/src/types.rs`. The strongest project-level identifiers around this patch are `amount`, `uncounted_stake`, `bond`, and `DelegationAction::Decrease`.

## Before/After Behavior

Before the patch, a new Decrease request was checked in isolation with bonded_amount - decrease_amount against MinDelegation, without evidence that already scheduled decreases for the same pair were included. Reward snapshot construction then added the pending decrease amount directly to uncounted_stake and used saturating_sub on bond.amount. After the patch, pending Decrease amounts are summed for cumulative MinDelegation validation, and reward snapshot accounting caps the decrease amount at bond.amount before updating uncounted_stake and rewardable bond amount.

# Root Cause

The request validation and reward snapshot paths handled pending delegation decreases inconsistently. Validation considered an individual decrease request, while snapshot accounting could operate on an aggregated decrease amount. When the aggregated amount exceeded the actual bond, the old snapshot code could count more uncounted stake than actually existed for that delegation.

## Walkthrough

1. A delegator can schedule Decrease requests for a collator/delegator pair.

2. The pre-fix request check validated the newly requested decrease against MinDelegation on its own.

3. Existing pending Decrease requests were not shown as part of that validation in the supplied evidence.

4. Later, reward snapshot construction handled pending Decrease actions for each bond.

5. The old snapshot code added the decrease amount directly to uncounted_stake while saturating the rewardable bond amount at zero.

6. If the pending decrease amount exceeded the actual bond, uncounted_stake could become larger than the delegation's real bonded stake.

7. The patch sums pending decreases during validation and caps snapshot accounting at bond.amount.

8. The added regression test name ties the scenario to snapshot denominator breakage and payout overmint prevention.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| pallets/parachain-staking/src/delegation_requests.rs | 222 | validates cumulative pending Decrease requests for a collator/delegator pair against MinDelegation before accepting another request |
| pallets/parachain-staking/src/lib.rs | 2212 | builds rewardable delegation snapshots and computes uncounted_stake for pending revoke/decrease actions used in payout accounting |
| pallets/parachain-staking/src/tests.rs | 364 | regression test covering stacked decrease requests, snapshot denominator integrity, and payout overmint prevention |

## Code Snippets

## Snippet 1

Context: `pallets/parachain-staking/src/delegation_requests.rs:222` (changes aggregate state or economic accounting)

Before
```rust
},
		);
		let new_amount: BalanceOf<T> = (bonded_amount - decrease_amount).into();
		ensure!(
			new_amount >= T::MinDelegation::get(),
			DispatchErrorWithPostInfo {
				post_info: Some(actual_weight).into(),
```
After
```rust
},
		);

		// Cumulative safety: multiple pending Decrease requests for the same
		// (collator, delegator) pair must also respect the MinDelegation
		// constraint when applied together. Otherwise, snapshots can become
		// inconsistent even if each request, in isolation, appears valid.
		let pending_decrease_total: BalanceOf<T> = scheduled_requests
```

## Snippet 2

Context: `pallets/parachain-staking/src/lib.rs:2212` (changes a sensitive control or state-update path)

Before
```rust
None => bond.amount,
						Some(DelegationAction::Revoke(_)) => {
							uncounted_stake = uncounted_stake.saturating_add(bond.amount);
							BalanceOf::<T>::zero()
						}
						Some(DelegationAction::Decrease(amount)) => {
							uncounted_stake = uncounted_stake.saturating_add(*amount);
							bond.amount.saturating_sub(*amount)
```
After
```rust
None => bond.amount,
						Some(DelegationAction::Revoke(_)) => {
							// For revokes, the entire current bond is excluded from rewards.
							uncounted_stake = uncounted_stake.saturating_add(bond.amount);
							BalanceOf::<T>::zero()
						}
						Some(DelegationAction::Decrease(amount)) => {
							// Multiple pending decreases for this (collator, delegator) pair
```

## Snippet 3

Context: `pallets/parachain-staking/src/tests.rs:364` (changes an authorization or privilege gate)

Before
```rust
}

// ~~ MONETARY GOVERNANCE ~~
```
After
```rust
}

#[test]
fn stacked_decrease_requests_cannot_break_snapshot_denominator_or_overmint_payout() {
	// `MinCandidateStk` and `MinDelegation` are associated types on the pallet
	// config and already implement `Get`, so we can use them directly without
	// importing the trait in the local scope.
	use sp_runtime::Perbill;
```

## Snippet 4

Context: `pallets/parachain-staking/src/tests.rs:34` (changes a sensitive control or state-update path)

Before
```rust
use crate::{
	assert_events_emitted, assert_events_emitted_match, assert_events_eq, assert_no_events,
	AtStake, Bond, CollatorStatus, DelegationScheduledRequests,
	DelegationScheduledRequestsPerCollator, DelegatorAdded, EnableMarkingOffline, Error, Event,
	FreezeReason, InflationDistributionInfo, Range, WasInactive,
};
use frame_support::migrations::SteppedMigration;
```
After
```rust
use crate::{
	assert_events_emitted, assert_events_emitted_match, assert_events_eq, assert_no_events,
	AtStake, AwardedPts, Bond, CollatorStatus, DelegationScheduledRequests,
	DelegationScheduledRequestsPerCollator, DelegatorAdded, EnableMarkingOffline, Error, Event,
	FreezeReason, InflationDistributionInfo, Points, Range, WasInactive,
};
use frame_support::migrations::SteppedMigration;
```

# Fix Pattern

Enforce the same monetary accounting invariant at both acceptance and aggregation points: validate cumulative pending decreases before accepting new requests, and cap derived reward accounting by the real bonded amount.

## How It Was Fixed

The delegation request path was changed to aggregate pending DelegationAction::Decrease amounts from scheduled_requests and apply MinDelegation to the cumulative total. The reward snapshot path was changed to compute capped = min(*amount, bond.amount), then use capped for both uncounted_stake and the adjusted rewardable bond amount. A regression test for stacked decrease requests, snapshot denominator integrity, and overmint prevention was added.

# Why It Matters

1. Preserves consistency between pending staking requests and real bonded stake.

2. Prevents uncounted_stake from exceeding the actual delegation bond.

3. Protects reward snapshot denominator accounting.

4. Evidence does not establish direct theft, maximum loss, or impact outside this staking reward path.

# Evidence Notes

The strongest evidence is the implementation change in pallets/parachain-staking/src/delegation_requests.rs adding cumulative pending Decrease handling, and the implementation change in pallets/parachain-staking/src/lib.rs capping uncounted_stake accounting by bond.amount. Patch comments explicitly mention inconsistent snapshots and corrupting the snapshot denominator. The added test name references overmint payout prevention. However, only snippets are provided, so confidence is downgraded from high to medium and the verdict from confirmed to likely. Protocol security invariant: Pending delegation decreases must be accounted for consistently with real bonded stake: cumulative decreases for a collator/delegator pair must not reduce the remaining delegation below MinDelegation, and uncounted_stake used in reward snapshot or payout denominator calculations must not exceed the actual bonded amount for that delegation. Verification notes: Does not prove direct theft by itself from the provided patch. Does not quantify maximum overmint or economic loss. Does not prove remote unauthenticated exploitability. Does not show consensus safety failure beyond staking reward/accounting inconsistency. Does not establish impact outside the parachain-staking delegation decrease and payout snapshot path. No full test body or payout formula is provided in the input. No exploit transaction sequence or economic impact bound is proven by the supplied evidence. The change is more than cleanup or refactor because it alters request validation and reward accounting behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-fix`
Keep in security corpus: `true`

The supplied patch evidence supports retaining this as a security-focused blockchain staking accounting fix. The implementation tightens cumulative validation of pending delegation decreases and caps reward snapshot uncounted stake by actual bonded amount. The added test name explicitly ties the bug to snapshot denominator breakage and payout overmint prevention. Exploitability and loss bounds are not proven, so the verdict remains likely rather than confirmed.

## Security Evidence

1. Delegation decrease validation was changed from checking only the new decrease to considering cumulative pending decreases for the same collator/delegator pair.
2. Reward snapshot accounting now caps decrease accounting at the real bond amount before adding to uncounted_stake.
3. Patch comments state that otherwise snapshots can become inconsistent and the snapshot denominator can be corrupted.
4. Regression test name references preventing stacked decrease requests from breaking the snapshot denominator or overminting payout.

## Missing Evidence

1. No full regression test body is provided.
2. No concrete exploit transaction sequence is shown.
3. No maximum overmint or economic loss bound is quantified.
4. No evidence proves impact outside the staking reward snapshot and payout path.

## Claim Boundaries

1. Supports a staking reward accounting security fix, not an access-control fix.
2. Supports possible payout overmint/state-integrity impact, not proven direct theft.
3. Does not establish remote unauthenticated exploitability.
4. Does not prove broader consensus failure beyond the shown staking accounting path.
