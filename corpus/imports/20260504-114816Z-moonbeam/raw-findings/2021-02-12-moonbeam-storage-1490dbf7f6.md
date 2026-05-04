---
case_id: case_20210212_1490dbf7f6
project: moonbeam
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
confidence: medium
source_quality: high
date: 2021-02-12
source_refs:
  - git:1490dbf7f6d33d3f50b47942ff87f8fb2b20736f
  - "pallets/stake/src/lib.rs:1178"
  - "pallets/stake/src/lib.rs:1097"
  - "pallets/stake/src/tests.rs:436"
  - "pallets/stake/src/tests.rs:831"
bug_class: historical-reward-accounting
impact_type:
  - reward-accounting-integrity
tags:
  - blockchain-core
  - staking
  - reward-accounting
  - validator
  - snapshot
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a staking reward accounting bug. `pay_stakers` previously used current `Candidates` state while paying rewards for an older round; after the patch it uses the round-indexed `AtStake` snapshot. This supports the narrower claim that nomination or validator state changes between earning and payout could affect historical reward distribution inputs.

## Observed Patch Facts

1. In `pallets/stake/src/lib.rs`, the patch replaces `// snapshot exposure for round` with `// snapshot exposure for round for weighting reward distribution`.

2. In `pallets/stake/src/lib.rs`, the patch replaces `if let Some(state) = <Candidates<T>>::get(&val) {` with `// Take the snapshot of block author and nominations`.

3. In `pallets/stake/src/tests.rs`, the patch replaces `fn payout_distribution_to_nominators() {` with `fn validator_commission() {`.

4. In `pallets/stake/src/tests.rs`, the patch adds `#[test]`.

## Project Context

The changed code sits primarily in `pallets/stake/src`, `pallets/stake`, which anchors the finding in the `storage` area of the project. Historical context from `pallets/stake/src/mock.rs`, `pallets/stake/src/set.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `pallets/stake/src/mock.rs`. The strongest project-level identifiers around this patch are `T::AccountId`, `state`, `RawEvent::ValidatorChosen`, and `exposure`.

## Before/After Behavior

Before the patch, delayed payout logic drained awarded points for `round_to_payout` but fetched current candidate state with `<Candidates<T>>::get(&val)` to decide whether the validator was solo and how to split rewards. After the patch, payout consumes `<AtStake<T>>::take(round_to_payout, &val)` and uses that snapshot's nominators, bond, and total. Validator selection also records exposure as `ValidatorSnapshot` for reward weighting.

# Root Cause

The payout path used live staking candidate state for historical reward distribution even though rewards are paid after a delay. The grounded root cause is missing or unused per-round exposure snapshots in reward settlement.

## Walkthrough

1. Validator selection chooses candidates and records per-round exposure for reward weighting.

2. Rewards are settled later after `BondDuration` by `pay_stakers` for `round_to_payout`.

3. Before the fix, `pay_stakers` read `<Candidates<T>>::get(&val)`, which reflects current staking state rather than the rewarded round's state.

4. If nominators revoked nominations or left before payout, the live candidate state could differ from the exposure that earned the rewards.

5. After the fix, payout uses `<AtStake<T>>::take(round_to_payout, &val)` and computes solo-validator handling and reward proportions from that snapshot.

6. Tests were added or updated around validator commission and revoke/leave nomination behavior.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| pallets/stake/src/lib.rs | 1079 | payout path now uses `AtStake` round snapshot instead of live `Candidates` state for validator/nominator reward distribution |
| pallets/stake/src/lib.rs | 1167 | validator election path records per-round validator exposure used later for reward weighting |
| pallets/stake/src/tests.rs | 831 | regression coverage for revoke nomination or leave nominators behavior across rounds |
| pallets/stake/src/tests.rs | 430 | reward distribution and validator commission expectations updated around snapshot-based payout behavior |

## Code Snippets

## Snippet 1

Context: `pallets/stake/src/lib.rs:1178` (changes a consensus- or validator-sensitive branch)

Before
```rust
.map(|x| x.owner)
			.collect::<Vec<T::AccountId>>();
		// snapshot exposure for round
		for account in validators.iter() {
			let state = <Candidates<T>>::get(&account)
				.expect("all members of CandidateQ must be viable candidates by construction; qed");
			let amount = state.total;
			let exposure: Exposure<T::AccountId, BalanceOf<T>> = state.into();
```
After
```rust
.map(|x| x.owner)
			.collect::<Vec<T::AccountId>>();
		// snapshot exposure for round for weighting reward distribution
		for account in validators.iter() {
			let state = <Candidates<T>>::get(&account)
				.expect("all members of CandidateQ must be candidates");
			let amount = state.total;
			let exposure: ValidatorSnapshot<T::AccountId, BalanceOf<T>> = state.into();
```

## Snippet 2

Context: `pallets/stake/src/lib.rs:1097` (changes an authorization or privilege gate)

Before
```rust
continue;
				}
				if let Some(state) = <Candidates<T>>::get(&val) {
					if state.nominators.0.is_empty() {
						// solo validator with no nominators
						mint(amt_due, val.clone());
					} else {
						// pay validator first; commission + due_portion
```
After
```rust
continue;
				}
				// Take the snapshot of block author and nominations
				let state = <AtStake<T>>::take(round_to_payout, &val);
				if state.nominators.is_empty() {
					// solo validator with no nominators
					mint(amt_due, val.clone());
				} else {
```

## Snippet 3

Context: `pallets/stake/src/tests.rs:436` (changes a consensus- or validator-sensitive branch)

Before
```rust
#[test]
fn payout_distribution_to_nominators() {
	five_validators_five_nominators().execute_with(|| {
		roll_to(4);
		roll_to(8);
		// chooses top MaxValidators (5), in order
		let mut expected = vec![
```
After
```rust
#[test]
fn validator_commission() {
	one_validator_two_nominators().execute_with(|| {
		roll_to(8);
		// chooses top MaxValidators (5), in order
```

## Snippet 4

Context: `pallets/stake/src/tests.rs:831` (changes a consensus- or validator-sensitive branch)

Before
```rust
});
}
```
After
```rust
});
}

#[test]
fn revoke_nomination_or_leave_nominators() {
	five_validators_five_nominators().execute_with(|| {
		roll_to(4);
		assert_noop!(
```

# Fix Pattern

Use round-indexed immutable accounting snapshots for delayed economic settlement instead of mutable live staking state.

## How It Was Fixed

The validator election path converts candidate state into `ValidatorSnapshot`, and `pay_stakers` now consumes the `AtStake` snapshot for the payout round. Reward distribution logic uses snapshot fields rather than current `Candidates` fields.

# Why It Matters

1. Preserves reward accounting integrity across delayed payout windows.

2. Prevents later nomination state from changing historical reward distribution inputs.

3. Keeps rewards tied to exposure active during the rewarded round.

4. Evidence supports economic misaccounting, not direct theft or access-control bypass.

# Evidence Notes

Strong evidence is the `pay_stakers` change from `<Candidates<T>>::get(&val)` to `<AtStake<T>>::take(round_to_payout, &val)`. The `best_candidates_become_validators` hunk supports snapshot-based reward weighting. The tests around commission and revoke/leave nominations support the behavioral area. The evidence does not prove arbitrary minting, unauthorized access, direct theft, consensus failure, or validator set corruption. Protocol security invariant: Staking rewards for a completed round should be distributed using the validator and nominator exposure recorded for that round, not mutable live candidate state observed at the later payout time. Verification notes: Patch evidence does not prove direct theft or arbitrary balance minting by an attacker. Patch evidence does not show unauthorized access control bypass. Patch evidence does not prove consensus halt or validator set corruption. Patch evidence does not establish whether the bug was exploitable intentionally versus causing incorrect reward accounting after normal nomination changes. Runtime version and serialization-related changes are not treated as security evidence. No external context or file inspection was used. Security classification is limited to likely staking reward accounting impact. Exploitability and attacker profit are not established by the supplied evidence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `historical-reward-accounting`
Final impact type: `reward-accounting-integrity`
Final tags: `blockchain-core, staking, reward-accounting, validator, snapshot`

The supplied patch evidence supports a conservative security-hardening classification, not a full security-fix claim. The staking payout path changed from reading mutable current candidate state to consuming a round-indexed AtStake snapshot when distributing delayed rewards, and tests cover revoke/leave nomination behavior. In a blockchain staking module this tightens an economic accounting invariant, but the evidence does not prove direct theft, arbitrary minting, privilege bypass, consensus failure, or a clearly exploitable attack.

## Security Evidence

1. pay_stakers now uses AtStake<T>::take(round_to_payout, &val) instead of Candidates<T>::get(&val) for payout state.
2. Validator exposure is explicitly snapshotted for reward distribution weighting.
3. The new/updated tests cover nomination revocation or leaving around round transitions.
4. The changed code is in staking reward distribution, a security-sensitive economic path in a blockchain runtime.

## Missing Evidence

1. No proof that an attacker could profit intentionally from the stale/live state mismatch.
2. No evidence of arbitrary balance minting or unauthorized withdrawal.
3. No evidence of access-control bypass or validator set corruption.
4. No explicit advisory, CVE, exploit scenario, or loss impact is supplied.

## Claim Boundaries

1. Retain only as staking reward accounting hardening.
2. Do not claim direct theft, arbitrary minting, or privilege escalation.
3. Do not claim consensus failure or validator-set corruption from this evidence alone.
4. The supported issue is delayed payout using current staking state instead of the rewarded round snapshot.
