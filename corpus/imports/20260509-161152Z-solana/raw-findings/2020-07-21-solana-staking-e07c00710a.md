---
case_id: case_20200721_e07c00710a
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2020-07-21
source_refs:
  - git:e07c00710a69ae69d60ae539339eb0f53e950452
  - "runtime/src/bank.rs:709"
  - "programs/stake/src/stake_state.rs:379"
  - "programs/stake/src/stake_state.rs:906"
  - "runtime/src/bank.rs:4538"
bug_class: reward-accounting-invariant
impact_type:
  - economic-integrity
  - state-integrity
confidence: medium
tags:
  - staking
  - rewards
  - accounting
  - consensus
  - validator
  - invariant-check
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes reward-accounting correctness in Solana's staking reward path. The evidence supports changes to reward value representation, staker/voter reward ordering, reward point calculation support, and post-payment assertions that compare observed paid rewards with recorded and allocated rewards. It does not establish an exploitable vulnerability or attacker-controlled path, so the security classification should remain unclear rather than confirmed or likely.

## Observed Patch Facts

1. In `runtime/src/bank.rs`, the patch replaces `let validator_rewards = self.pay_validator_rewards(validator_point_value);` with `let validator_rewards_paid =`.

2. In `programs/stake/src/stake_state.rs`, the patch replaces `point_value: f64,` with `point_value: &PointValue,`.

3. In `programs/stake/src/stake_state.rs`, the patch replaces `// utility function, used by runtime::Stakes, tests` with `// utility function, used by runtime`.

4. In `runtime/src/bank.rs`, the patch replaces `let validator_points = bank.stakes.read().unwrap().points();` with `let validator_points: u128 = bank`.

## Project Context

The changed code sits primarily in `runtime/src`, `programs/stake/src`, `programs/stake`, which anchors the finding in the `staking` area of the project. Historical context from `runtime/src/stakes.rs`, `runtime/src/bank_client.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/stakes.rs`, `runtime/src/genesis_utils.rs`. The strongest project-level identifiers around this patch are `vote_account`, `vote_state`, `stake_history`, and `stake_account`.

## Before/After Behavior

Before the patch, reward redemption accepted an f64 point value, mapped calculate_rewards output in the opposite staker/voter order shown after the patch, and Bank::update_rewards lacked the shown post-payment checks comparing actual paid rewards to recorded rewards and the allocated validator reward amount. After the patch, redemption takes a PointValue reference, applies and returns staker/voter rewards in the corrected order, adds a runtime-facing calculate_points helper, and Bank::update_rewards derives validator_rewards_paid from the change in vote_balance_and_staked and asserts consistency with recorded rewards and the allocation cap.

# Root Cause

The grounded root cause is inconsistent or insufficiently checked reward accounting in the staking rewards path, including reward split ordering, numeric representation of point value, and lack of explicit post-payment validation against the allocated validator reward amount. The evidence does not prove malicious exploitability.

## Walkthrough

1. Bank::update_rewards calculates the validator reward amount for an epoch.

2. The patched code records vote_balance_and_staked before reward payment and recomputes it afterward.

3. The difference is treated as validator_rewards_paid.

4. When rewards records are present, the patched code asserts that the observed paid amount equals the recorded rewards sum.

5. The patched code also asserts that observed paid rewards do not exceed the allocated validator_rewards amount.

6. Stake::redeem_rewards now takes a PointValue reference instead of an f64 point value.

7. Stake::redeem_rewards now maps calculate_rewards output as stakers_reward, voters_reward, credits_observed and applies stakers_reward to the delegation stake.

8. A calculate_points helper was added to derive points from stake and vote account state.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 679 | epoch reward distribution computes validator reward allocation and applies reward payment |
| runtime/src/bank.rs | 709 | post-payment accounting check compares paid validator rewards against recorded rewards and allocated amount |
| programs/stake/src/stake_state.rs | 379 | stake reward redemption uses PointValue and applies staker/voter reward split to stake state |
| programs/stake/src/stake_state.rs | 881 | redeem_rewards mutates stake and vote account lamports based on calculated rewards |
| programs/stake/src/stake_state.rs | 906 | runtime-facing reward point calculation from stake and vote accounts |
| runtime/src/stakes.rs | 1 | stake/vote account cache used to derive stake and reward-related totals |

## Code Snippets

## Snippet 1

Context: `runtime/src/bank.rs:709` (changes a consensus- or validator-sensitive branch)

Before
```rust
});

        let validator_rewards = self.pay_validator_rewards(validator_point_value);

        self.capitalization
            .fetch_add(validator_rewards as u64, Ordering::Relaxed);
    }
```
After
```rust
});

        let validator_rewards_paid =
            self.stakes.read().unwrap().vote_balance_and_staked() - vote_balance_and_staked;
        if let Some(rewards) = self.rewards.as_ref() {
            assert_eq!(
                validator_rewards_paid,
                u64::try_from(rewards.iter().map(|(_pubkey, reward)| reward).sum::<i64>()).unwrap()
```

## Snippet 2

Context: `programs/stake/src/stake_state.rs:379` (changes a consensus- or validator-sensitive branch)

Before
```rust
pub fn redeem_rewards(
        &mut self,
        point_value: f64,
        vote_state: &VoteState,
        stake_history: Option<&StakeHistory>,
    ) -> Option<(u64, u64)> {
        self.calculate_rewards(point_value, vote_state, stake_history)
            .map(|(voters_reward, stakers_reward, credits_observed)| {
```
After
```rust
pub fn redeem_rewards(
        &mut self,
        point_value: &PointValue,
        vote_state: &VoteState,
        stake_history: Option<&StakeHistory>,
    ) -> Option<(u64, u64)> {
        self.calculate_rewards(point_value, vote_state, stake_history)
            .map(|(stakers_reward, voters_reward, credits_observed)| {
```

## Snippet 3

Context: `programs/stake/src/stake_state.rs:906` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

// utility function, used by runtime::Stakes, tests
pub fn new_stake_history_entry<'a, I>(
```
After
```rust
}

// utility function, used by runtime
pub fn calculate_points(
    stake_account: &Account,
    vote_account: &Account,
    stake_history: Option<&StakeHistory>,
) -> Result<u128, InstructionError> {
```

## Snippet 4

Context: `runtime/src/bank.rs:4538` (changes a consensus- or validator-sensitive branch)

Before
```rust
bank.store_account(&vote_id, &vote_account);

        let validator_points = bank.stakes.read().unwrap().points();

        // put a child bank in epoch 1, which calls update_rewards()...
```
After
```rust
bank.store_account(&vote_id, &vote_account);

        let validator_points: u128 = bank
            .stake_delegation_accounts()
            .iter()
            .flat_map(|(_vote_pubkey, (stake_group, vote_account))| {
                stake_group
                    .iter()
```

# Fix Pattern

Tighten reward accounting by using structured reward value handling, correcting reward tuple ordering, deriving/checking reward amounts explicitly, and adding assertions for post-payment consistency.

## How It Was Fixed

The patch changed reward redemption from f64 point values to PointValue references, corrected the staker/voter reward tuple mapping, added a calculate_points helper for stake/vote account based point calculation, and added Bank::update_rewards assertions that the observed reward balance delta matches recorded rewards and does not exceed the allocated validator reward amount.

# Why It Matters

1. Epoch rewards affect consensus-visible account balances.

2. Incorrect reward ordering can credit the wrong account side.

3. Overpayment checks protect the reward allocation invariant.

4. The evidence supports correctness and possible security relevance, but not a proven vulnerability.

# Evidence Notes

Supported by the supplied hunks in runtime/src/bank.rs around update_rewards and post-payment assertions, programs/stake/src/stake_state.rs around redeem_rewards and calculate_points, and the updated reward test. Unsupported claims removed: remote exploitability, intentional validator-triggered overpayment, quantified supply inflation, unauthorized account access, or confirmed vulnerability status. Protocol security invariant: Epoch validator reward distribution should compute rewards deterministically from stake and vote state, apply the staker/voter split consistently, and avoid paying more rewards than the amount allocated for the epoch. Verification notes: The patch does not prove remote exploitability. The patch does not show an unauthorized account access or signature bypass. The patch does not prove a validator could intentionally trigger overpayment. The patch does not quantify any possible overpayment or supply divergence. Some changes may be correctness and determinism fixes rather than independently exploitable vulnerabilities. No external context or file inspection was used. Classification is conservative because the provided evidence shows accounting fixes but not an exploit path. Helper additions are treated as support code, not as the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `reward-accounting-invariant`
Final impact type: `economic-integrity, state-integrity`
Final confidence: `medium`
Final tags: `staking, rewards, accounting, consensus, validator, invariant-check`

The supplied patch evidence supports a conservative security-hardening classification, not a confirmed vulnerability fix. The changes tighten staking reward accounting in a consensus-visible economic path by replacing floating-point reward value handling, correcting staker/voter reward ordering, deriving reward points from account state, and adding assertions that paid validator rewards match recorded rewards and do not exceed the allocated amount. The evidence does not prove exploitability, attacker control, or an observed security incident, so it should not be treated as a security-fix.

## Security Evidence

1. Patch adds a post-payment assertion that validator rewards paid do not exceed allocated validator rewards.
2. Patch checks observed paid rewards against the recorded rewards sum when rewards records exist.
3. Reward calculation and redemption occur in staking/runtime code that affects consensus-visible balances.
4. The commit explicitly mentions verifying that rewards spending does not exceed the allocated reward amount.
5. The patch removes f64 reward point handling in favor of structured/integer-oriented accounting.

## Missing Evidence

1. No evidence of attacker-controlled inputs causing overpayment.
2. No proof of remote exploitability or privilege bypass.
3. No quantified inflation, theft, or account corruption impact is shown.
4. No advisory, CVE, or security-labeled commit message is provided.
5. No evidence that the stale or incorrect reward state could be intentionally triggered by a validator or user.

## Claim Boundaries

1. Classify as hardening of staking reward accounting invariants, not as a proven exploit fix.
2. Do not claim signature bypass, authorization failure, or unauthorized account access.
3. Do not claim confirmed supply inflation or theft from the supplied patch alone.
4. Do not treat the test-only reward point recalculation as independent security evidence.
5. The strongest supported claim is prevention/detection of inconsistent or excessive reward distribution.
