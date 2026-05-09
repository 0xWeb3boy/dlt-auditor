---
case_id: case_20201215_db339cb925
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2020-12-15
source_refs:
  - git:db339cb9258611d3e29f74d366deffeff322e449
  - "core/src/replay_stage.rs:2590"
  - "runtime/src/bank.rs:2260"
  - "runtime/src/bank.rs:2272"
  - "core/src/replay_stage.rs:2543"
bug_class: consensus-state-ordering-race
impact_type:
  - consensus-integrity-risk
tags:
  - blockchain-core
  - consensus
  - validator
  - replay
  - accounts-hash
  - race-condition
  - state-ordering
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a consensus-relevant race in Solana's bank runtime. `Bank::register_tick` previously made the boundary tick height visible before completing blockhash queue and recent blockhashes sysvar updates, while ReplayStage could use that boundary tick height as the signal to begin accounts delta hash calculation. The patch reorders the tick-height increment after those updates and strengthens the guard to reject tick registration once freezing has started.

## Observed Patch Facts

1. In `core/src/replay_stage.rs`, the patch replaces `let bank1 = Bank::new_from_parent(&arc_bank0, &Pubkey::default(), arc_bank0.slot() + 1);` with `for i in 1..=3 {`.

2. In `runtime/src/bank.rs`, the patch replaces `!self.is_frozen(),` with `!self.freeze_started(),`.

3. In `runtime/src/bank.rs`, the patch adds `// ReplayStage will start computing the accounts delta hash when it`.

4. In `core/src/replay_stage.rs`, the patch replaces `fn leader_vote(bank: &Arc<Bank>, pubkey: &Pubkey) {` with `fn leader_vote(vote_slot: Slot, bank: &Arc<Bank>, pubkey: &Pubkey) {`.

## Project Context

The changed code sits primarily in `core/src`, `runtime/src`, which anchors the finding in the `consensus` area of the project. Historical context from `runtime/src/bank_forks.rs`, `core/src/optimistically_confirmed_bank_tracker.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank_forks.rs`, `core/src/poh_recorder.rs`. The strongest project-level identifiers around this patch are `bank`, `Bank::new_from_parent`, `Pubkey::default`, and `unwrap`.

## Before/After Behavior

Before the patch, `register_tick` asserted only `!self.is_frozen()`, incremented `tick_height` before the slot-boundary update block, and then used the incremented value to decide whether to register the boundary blockhash and update recent blockhashes. After the patch, it asserts `!self.freeze_started()`, checks whether the next tick reaches a block boundary before incrementing `tick_height`, performs the blockhash queue and recent blockhashes update work first, and increments `tick_height` last. ReplayStage tests were also broadened to cover multi-slot fork and vote behavior, but those test changes are supporting evidence rather than the root fix.

# Root Cause

The supported root cause is an ordering race in `Bank::register_tick`: boundary tick height could become visible before slot-boundary blockhash-related updates were complete. The added code comment ties that ordering directly to ReplayStage starting accounts delta hash computation when it observes the boundary tick height. The previous `is_frozen()` guard also left a narrower lifecycle window where tick registration could proceed after freezing had started but before the bank was fully frozen.

## Walkthrough

1. `Bank::register_tick` records ticks and performs block-boundary blockhash-related updates.

2. Before the patch, the function rejected only fully frozen banks with `!self.is_frozen()`.

3. Before the patch, `tick_height.fetch_add(1, Relaxed)` happened before the block-boundary update logic.

4. ReplayStage can begin accounts delta hash computation after observing that tick height has reached the boundary.

5. That creates a race where hash calculation may start before the boundary blockhash queue and recent blockhashes sysvar updates are committed.

6. The patch changes the guard to `!self.freeze_started()`.

7. The patch performs the block-boundary update logic before incrementing `tick_height`.

8. The added comment explicitly documents the ReplayStage/accounts-delta-hash ordering dependency.

9. ReplayStage test changes exercise multi-slot behavior, but they do not independently prove exploitability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 2260 | `Bank::register_tick` enforces tick registration ordering and prevents tick registration while freeze is in progress. |
| runtime/src/bank.rs | 2272 | Boundary tick height is incremented only after blockhash queue and recent blockhashes sysvar updates are committed, preserving the accounts hash input ordering. |
| core/src/replay_stage.rs | 2590 | ReplayStage test setup now builds and advances multiple fork banks, exercising slot-boundary behavior relevant to commitment and replay. |
| core/src/replay_stage.rs | 2543 | Test vote helper now accepts an explicit voted slot, supporting multi-slot replay/commitment scenarios. |

## Code Snippets

## Snippet 1

Context: `core/src/replay_stage.rs:2590` (changes signature or replay validation logic)

Before
```rust
.is_none());

        let bank1 = Bank::new_from_parent(&arc_bank0, &Pubkey::default(), arc_bank0.slot() + 1);
        let _res = bank1.transfer(
            10,
            &genesis_config_info.mint_keypair,
            &solana_sdk::pubkey::new_rand(),
        );
```
After
```rust
.is_none());

        for i in 1..=3 {
            let prev_bank = bank_forks.read().unwrap().get(i - 1).unwrap().clone();
            let bank = Bank::new_from_parent(&prev_bank, &Pubkey::default(), prev_bank.slot() + 1);
            let _res = bank.transfer(
                10,
                &genesis_config_info.mint_keypair,
```

## Snippet 2

Context: `runtime/src/bank.rs:2260` (changes a sensitive control or state-update path)

Before
```rust
pub fn register_tick(&self, hash: &Hash) {
        assert!(
            !self.is_frozen(),
            "register_tick() working on a frozen bank!"
        );

        inc_new_counter_debug!("bank-register_tick-registered", 1);
        // Grab blockhash lock before incrementing tick height so that replay stage does
```
After
```rust
pub fn register_tick(&self, hash: &Hash) {
        assert!(
            !self.freeze_started(),
            "register_tick() working on a bank that is already frozen or is undergoing freezing!"
        );

        inc_new_counter_debug!("bank-register_tick-registered", 1);
        let mut w_blockhash_queue = self.blockhash_queue.write().unwrap();
```

## Snippet 3

Context: `runtime/src/bank.rs:2272` (changes a sensitive control or state-update path)

Before
```rust
}
        }
    }
```
After
```rust
}
        }
        // ReplayStage will start computing the accounts delta hash when it
        // detects the tick height has reached the boundary, so the system
        // needs to guarantee all account updates for the slot have been
        // committed before this tick height is incremented (like the blockhash
        // sysvar above)
        self.tick_height.fetch_add(1, Relaxed);
```

## Snippet 4

Context: `core/src/replay_stage.rs:2543` (changes a consensus- or validator-sensitive branch)

Before
```rust
#[test]
    fn test_replay_commitment_cache() {
        fn leader_vote(bank: &Arc<Bank>, pubkey: &Pubkey) {
            let mut leader_vote_account = bank.get_account(&pubkey).unwrap();
            let mut vote_state = VoteState::from(&leader_vote_account).unwrap();
            vote_state.process_slot_vote_unchecked(bank.slot());
            let versioned = VoteStateVersions::Current(Box::new(vote_state));
            VoteState::to(&versioned, &mut leader_vote_account).unwrap();
```
After
```rust
#[test]
    fn test_replay_commitment_cache() {
        fn leader_vote(vote_slot: Slot, bank: &Arc<Bank>, pubkey: &Pubkey) {
            let mut leader_vote_account = bank.get_account(&pubkey).unwrap();
            let mut vote_state = VoteState::from(&leader_vote_account).unwrap();
            vote_state.process_slot_vote_unchecked(vote_slot);
            let versioned = VoteStateVersions::Current(Box::new(vote_state));
            VoteState::to(&versioned, &mut leader_vote_account).unwrap();
```

# Fix Pattern

Delay publication of the externally observed boundary state until dependent state updates are complete, and strengthen the lifecycle guard around freeze-sensitive mutation.

## How It Was Fixed

`register_tick` now checks `freeze_started()` instead of only `is_frozen()`. It determines whether the next tick is a block boundary before incrementing `tick_height`, performs blockhash queue registration and optional recent blockhashes sysvar updates first, then increments `tick_height` after those updates. Tests in `core/src/replay_stage.rs` were adjusted to cover multiple fork banks and explicit voted slots.

# Why It Matters

1. Accounts hash calculation is consensus-sensitive.

2. ReplayStage treats boundary tick height as a signal to begin hash work.

3. Publishing tick height too early can expose partially updated slot-boundary state.

4. Preventing tick registration during freeze reduces overlap with hash/freeze logic.

5. The evidence supports consensus-safety risk, but not funds theft, signature bypass, or proven remote exploitability.

# Evidence Notes

Primary evidence is the `runtime/src/bank.rs` change in `register_tick`: `!self.is_frozen()` becomes `!self.freeze_started()`, the boundary check changes to use `self.tick_height.load(Relaxed) + 1`, and `self.tick_height.fetch_add(1, Relaxed)` is moved after blockhash queue and recent blockhashes update logic. The strongest explanatory evidence is the added comment stating that ReplayStage starts computing the accounts delta hash when tick height reaches the boundary and that all account updates for the slot must be committed before incrementing tick height. The `core/src/replay_stage.rs` changes are test support, not root-cause code. The evidence does not establish attacker control, practical exploitability, funds theft, authorization bypass, or a deterministic consensus split. Protocol security invariant: At a slot boundary, tick height must not become observable as complete until the slot-boundary bank state updates needed for accounts hashing, including blockhash-related updates, have been committed. Tick registration also should not proceed once bank freezing has started, because freeze/account-hash work expects stable bank state. Verification notes: The patch does not prove remote exploitability. The patch does not show an intentional adversarial transaction sequence. The patch does not prove funds theft, signature bypass, or account authorization failure. The patch does not prove a deterministic consensus split, only a race affecting consensus-critical hashing/order. Test-only changes in `core/src/replay_stage.rs` are supporting evidence, not the root fix. Classified as likely rather than confirmed because exploitability and observed consensus divergence are not shown. Kept in the security corpus because the race affects consensus-critical account-hash ordering, not merely cleanup or refactor work. Downgraded claims to avoid asserting remote exploitability or deterministic fork/split behavior. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-state-ordering-race`
Final impact type: `consensus-integrity-risk`
Final tags: `blockchain-core, consensus, validator, replay, accounts-hash, race-condition, state-ordering`

The evidence supports retaining this as security hardening, not a confirmed security fix. The patch changes a consensus-sensitive Solana bank tick path so the boundary tick height is not published before blockhash/sysvar updates complete, and it tightens mutation during bank freezing. The added comment directly ties the ordering to ReplayStage accounts delta hash computation. However, the patch does not prove attacker control, exploitability, or an observed consensus failure, so the original security-fix framing is too strong.

## Security Evidence

1. Commit subject identifies a race between tick height publication and accounts hash calculation.
2. `Bank::register_tick` now rejects work once freezing has started, not only after the bank is frozen.
3. `tick_height.fetch_add` is moved after blockhash queue and recent blockhashes sysvar updates.
4. Added comment states ReplayStage starts accounts delta hash computation when boundary tick height is observed.
5. Changed path is in runtime/replay logic for validator consensus-critical bank state.

## Missing Evidence

1. No demonstrated exploit path or adversarial input sequence.
2. No evidence of observed network consensus split or deterministic validator divergence.
3. No proof of funds loss, authorization bypass, or signature validation failure.
4. ReplayStage changes shown are primarily test support and do not independently prove exploitability.

## Claim Boundaries

1. Classify as consensus security hardening rather than a confirmed exploitable vulnerability.
2. Do not claim remote exploitability from this patch alone.
3. Do not claim deterministic consensus failure or chain split from the supplied evidence.
4. Do not retain unsupported tags such as snapshot, RPC, or generic queue unless separately evidenced.
