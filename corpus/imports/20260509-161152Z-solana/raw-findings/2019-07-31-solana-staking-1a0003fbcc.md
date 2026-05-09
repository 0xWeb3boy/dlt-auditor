---
case_id: case_20190731_1a0003fbcc
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: staking
source_quality: high
date: 2019-07-31
source_refs:
  - git:1a0003fbcc1ffdb15e5283f4cb0f5c31b33c62f5
  - "programs/stake_api/src/stake_state.rs:288"
  - "runtime/src/bank.rs:2438"
  - "runtime/src/bank.rs:2489"
  - "runtime/src/bank.rs:2507"
bug_class: stake-withdrawal-epoch-accounting-hardening
impact_type:
  - stake-accounting-integrity
  - withdrawal-policy-enforcement
confidence: medium
tags:
  - staking
  - withdrawal
  - epoch-accounting
  - stake-accounting
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Solana staking epoch accounting behavior. In stake_state.rs, withdraw now rejects a StakeState::Stake account with stake.deactivated == std::u64::MAX before calculating staked balance, and then uses stake.stake(clock.stakers_epoch) instead of stake.stake(clock.epoch). The bank.rs changes shown are tests that query epoch_vote_accounts(epoch) and assert expected stake weights. This may be security relevant because staking and vote weights are consensus-sensitive, but the supplied evidence does not prove exploitability, unauthorized withdrawal, stolen funds, or a consensus failure.

## Observed Patch Facts

1. In `programs/stake_api/src/stake_state.rs`, the patch replaces `let staked = if stake.stake(clock.epoch) == 0 {` with `// still activated, no can do`.

2. In `runtime/src/bank.rs`, the patch replaces `let vote_accounts0: Option<HashMap<_, _>> = parent.epoch_vote_accounts(0).map(|accoun...` with `let mut leader_vote_stake: Vec<_> = parent`.

3. In `runtime/src/bank.rs`, the patch replaces `assert!(child.epoch_vote_accounts(i).is_some());` with `assert!(child.epoch_vote_accounts(epoch).is_some());`.

4. In `runtime/src/bank.rs`, the patch replaces `assert!(child.epoch_vote_accounts(i).is_some());` with `assert!(child.epoch_vote_accounts(epoch).is_some());`.

## Project Context

The changed code sits primarily in `programs/stake_api/src`, `programs/stake_api`, `runtime/src`, which anchors the finding in the `staking` area of the project. Historical context from `runtime/src/stakes.rs`, `programs/stake_api/src/stake_instruction.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/stakes.rs`, `runtime/src/lib.rs`. The strongest project-level identifiers around this patch are `stake`, `epoch`, `epoch_vote_accounts`, and `child`.

## Before/After Behavior

Before the patch, the shown withdraw path computed staked using stake.stake(clock.epoch) without the visible explicit still-activated rejection. After the patch, it returns InstructionError::InsufficientFunds when stake.deactivated is std::u64::MAX, then computes staked using clock.stakers_epoch. The runtime test expectations changed from checking epoch_vote_accounts(i) to checking epoch_vote_accounts(epoch), with an added assertion that stored leader vote-account stake equals leader_stake.stake(epoch).

# Root Cause

The grounded root cause is an epoch-basis mismatch or incomplete guard in staking accounting: the old shown code used clock.epoch for the withdrawal staked-balance calculation, while the fixed code uses clock.stakers_epoch and explicitly rejects still-activated stake. The evidence does not establish that this mismatch allowed a security breach.

## Walkthrough

1. A stake account withdraw operation reaches stake_state.rs::withdraw and matches StakeState::Stake.

2. The old shown code calculated staked with stake.stake(clock.epoch).

3. The patch adds a guard that rejects stake.deactivated == std::u64::MAX with InstructionError::InsufficientFunds.

4. The patched code calculates staked with stake.stake(clock.stakers_epoch).

5. The bank tests now check epoch_vote_accounts(epoch), not epoch_vote_accounts(i).

6. The tests also verify that a leader vote account's stored stake matches leader_stake.stake(epoch).

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| programs/stake_api/src/stake_state.rs | 278 | stake withdraw eligibility and staked-balance calculation now use activation status and stakers_epoch |
| runtime/src/bank.rs | 2425 | epoch_vote_accounts test setup derives vote-account stake weights for the leader |
| runtime/src/bank.rs | 2483 | test asserts epoch_vote_accounts exists for the target epoch and carries the expected stake |
| runtime/src/bank.rs | 2501 | test verifies epoch stake generation when crossing the epoch boundary |
| runtime/src/stakes.rs | 1 | stake/vote-account cache used to derive node stakes |

## Code Snippets

## Snippet 1

Context: `programs/stake_api/src/stake_state.rs:288` (changes a consensus- or validator-sensitive branch)

Before
```rust
match self.state()? {
            StakeState::Stake(mut stake) => {
                let staked = if stake.stake(clock.epoch) == 0 {
                    0
                } else {
```
After
```rust
match self.state()? {
            StakeState::Stake(mut stake) => {
                // still activated, no can do
                if stake.deactivated == std::u64::MAX {
                    return Err(InstructionError::InsufficientFunds);
                }
                let staked = if stake.stake(clock.stakers_epoch) == 0 {
                    0
```

## Snippet 2

Context: `runtime/src/bank.rs:2438` (changes a consensus- or validator-sensitive branch)

Before
```rust
let parent = Arc::new(Bank::new(&genesis_block));

        let vote_accounts0: Option<HashMap<_, _>> = parent.epoch_vote_accounts(0).map(|accounts| {
            accounts
                .iter()
                .filter_map(|(pubkey, (_, account))| {
                    if let Ok(vote_state) = VoteState::deserialize(&account.data) {
```
After
```rust
let parent = Arc::new(Bank::new(&genesis_block));
        let mut leader_vote_stake: Vec<_> = parent
            .epoch_vote_accounts(0)
            .map(|accounts| {
                accounts
                    .iter()
                    .filter_map(|(pubkey, (stake, account))| {
```

## Snippet 3

Context: `runtime/src/bank.rs:2489` (changes a consensus- or validator-sensitive branch)

Before
```rust
);

        assert!(child.epoch_vote_accounts(i).is_some());

        // child crosses epoch boundary but isn't the first slot in the epoch
        let child = Bank::new_from_parent(
            &parent,
```
After
```rust
);

        assert!(child.epoch_vote_accounts(epoch).is_some());
        assert_eq!(
            leader_stake.stake(epoch),
            child
                .epoch_vote_accounts(epoch)
                .unwrap()
```

## Snippet 4

Context: `runtime/src/bank.rs:2507` (changes a consensus- or validator-sensitive branch)

Before
```rust
SLOTS_PER_EPOCH - (STAKERS_SLOT_OFFSET % SLOTS_PER_EPOCH) + 1,
        );
        assert!(child.epoch_vote_accounts(i).is_some());
    }
```
After
```rust
SLOTS_PER_EPOCH - (STAKERS_SLOT_OFFSET % SLOTS_PER_EPOCH) + 1,
        );
        assert!(child.epoch_vote_accounts(epoch).is_some());
    }
```

# Fix Pattern

Use the protocol's intended epoch snapshot for stake accounting and add an explicit guard for still-active stake before withdrawal calculations proceed.

## How It Was Fixed

The implementation changed the withdraw calculation from clock.epoch to clock.stakers_epoch and added an active-stake rejection. The tests were updated to validate epoch_vote_accounts for the target epoch and expected stake weight.

# Why It Matters

1. Stake accounting affects validator vote weights and withdrawal eligibility.

2. Using the wrong epoch basis can produce inconsistent stake snapshots.

3. The patch touches consensus-sensitive code, but the security impact is not demonstrated.

4. No concrete attacker path or loss scenario is provided.

# Evidence Notes

Primary implementation evidence is the stake_state.rs withdraw hunk. The bank.rs evidence shown is test code. The supplied context supports an epoch stake accounting fix, but does not show a concrete exploit, unauthorized withdrawal, funds theft, or network-level consensus failure. Claims that this is a confirmed or likely vulnerability are stronger than the provided evidence supports. Protocol security invariant: Stake withdrawal eligibility and epoch vote-account stake snapshots should be evaluated against the intended protocol epoch basis, and still-activated stake should not be treated as freely withdrawable. The provided evidence supports this as an accounting invariant, but does not establish a concrete security violation. Verification notes: No concrete attacker transaction sequence is shown by the patch evidence. No proof is provided that funds could be stolen, only that active stake withdrawal/accounting rules were tightened. No network-level consensus failure is demonstrated, though the path is consensus-sensitive. Most runtime changes shown are tests, so the implementation evidence is strongest in stake_state.rs. Verified from provided input only. No commands, file inspection, or external context were used. Security classification downgraded because exploitability is not established. Helper or test changes were treated as supporting evidence, not root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `stake-withdrawal-epoch-accounting-hardening`
Final impact type: `stake-accounting-integrity, withdrawal-policy-enforcement`
Final confidence: `medium`
Final tags: `staking, withdrawal, epoch-accounting, stake-accounting, security-hardening`

The supplied evidence does not prove a concrete exploit, theft, or consensus failure, so this should not be treated as a confirmed security fix. However, the implementation hunk clearly tightens a security-sensitive staking withdrawal path by rejecting still-active stake accounts and changing the stake calculation to the stakers epoch. In a blockchain staking subsystem, withdrawal eligibility and stake snapshot accounting are security-relevant invariants, so the evidence supports retaining this as conservative security hardening rather than a vulnerability fix.

## Security Evidence

1. Stake withdrawal now explicitly rejects StakeState::Stake when stake.deactivated == std::u64::MAX.
2. The rejected condition is labeled in-code as still activated, no can do, indicating a withdrawal eligibility guard.
3. The staked balance calculation changed from clock.epoch to clock.stakers_epoch, aligning withdrawal accounting with the staking epoch basis.
4. Runtime tests assert epoch_vote_accounts for the target epoch and validate expected leader stake weight.

## Missing Evidence

1. No attacker transaction sequence is shown.
2. No evidence proves unauthorized withdrawal, stolen funds, or bypass of signer checks.
3. No demonstrated consensus split or validator vote-weight manipulation is provided.
4. Most runtime evidence is test-only rather than production logic.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Do not claim exploitability or fund theft from the supplied patch alone.
3. Do not claim a consensus failure; only epoch stake accounting hardening is supported.
4. The strongest supported claim is tightened stake withdrawal and epoch accounting behavior.
