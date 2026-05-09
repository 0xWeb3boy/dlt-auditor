---
case_id: case_20201215_ef9f54b3d4
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
impact_type:
  - consensus-failure
confidence: medium
source_quality: high
date: 2020-12-15
source_refs:
  - git:ef9f54b3d4e04ff91c702345344cfb932360ee82
  - "core/src/replay_stage.rs:2606"
  - "runtime/src/bank.rs:2293"
  - "runtime/src/bank.rs:2305"
  - "core/src/replay_stage.rs:2559"
bug_class: consensus-state-race
tags:
  - blockchain-core
  - consensus
  - validator
  - replay
  - race-condition
  - accounts-hash
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a consensus-runtime race in Solana Bank tick registration. The grounded evidence is that tick_height was previously advanced before the blockhash/recent-blockhash sysvar boundary work completed, while the added comment states ReplayStage begins accounts delta hash calculation after observing the boundary tick height. The patch reorders tick publication after those updates and rejects tick registration once freezing has started.

## Observed Patch Facts

1. In `core/src/replay_stage.rs`, the patch replaces `let bank1 = Bank::new_from_parent(&arc_bank0, &Pubkey::default(), arc_bank0.slot() + 1);` with `for i in 1..=3 {`.

2. In `runtime/src/bank.rs`, the patch replaces `!self.is_frozen(),` with `!self.freeze_started(),`.

3. In `runtime/src/bank.rs`, the patch adds `// ReplayStage will start computing the accounts delta hash when it`.

4. In `core/src/replay_stage.rs`, the patch replaces `fn leader_vote(bank: &Arc<Bank>, pubkey: &Pubkey) {` with `fn leader_vote(vote_slot: Slot, bank: &Arc<Bank>, pubkey: &Pubkey) {`.

## Project Context

The changed code sits primarily in `core/src`, `runtime/src`, which anchors the finding in the `consensus` area of the project. Historical context from `runtime/src/bank_forks.rs`, `core/src/optimistically_confirmed_bank_tracker.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank_forks.rs`, `core/src/poh_recorder.rs`. The strongest project-level identifiers around this patch are `bank`, `Bank::new_from_parent`, `Pubkey::default`, and `unwrap`.

## Before/After Behavior

Before the patch, register_tick only rejected already-frozen banks and advanced tick_height before completing the block-boundary blockhash/sysvar update path. After the patch, register_tick rejects banks where freezing has started, performs boundary blockhash and recent-blockhash sysvar updates first, and increments tick_height only afterward. The replay_stage hunks appear to be test coverage changes rather than the root runtime fix.

# Root Cause

An ordering race in Bank::register_tick: tick_height served as a signal to ReplayStage, but it could be incremented before all state needed for the slot boundary and accounts hash calculation was committed. The previous is_frozen guard also did not cover the period where freezing had started but was not complete.

## Walkthrough

1. Bank::register_tick handles ticks in the runtime path used by replay/PoH processing.

2. Before the fix, the function asserted only that the bank was not fully frozen.

3. The old ordering advanced tick_height before completing block-boundary blockhash and recent-blockhash sysvar updates.

4. The patch comment states ReplayStage starts computing the accounts delta hash when it observes the boundary tick height.

5. That made tick_height an observable publication signal for downstream freeze/hash work.

6. The fix checks the next boundary using the current tick height, completes blockhash/sysvar work, and only then increments tick_height.

7. The guard was strengthened from is_frozen to freeze_started to block tick registration once freezing is underway.

8. The core replay_stage changes are best treated as tests/supporting coverage.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 2293 | Primary fix in Bank::register_tick: prevents tick registration during freeze start and reorders boundary tick publication after blockhash/sysvar updates. |
| runtime/src/bank.rs | 2305 | Adds explicit ordering invariant before tick_height.fetch_add so ReplayStage cannot observe the boundary before account updates are committed. |
| core/src/replay_stage.rs | 2559 | Test helper adjusted to vote on explicit slots while exercising replay commitment behavior. |
| core/src/replay_stage.rs | 2606 | Test setup expands chained bank fork progression across slots to cover replay/commitment behavior around frozen banks. |

## Code Snippets

## Snippet 1

Context: `core/src/replay_stage.rs:2606` (changes signature or replay validation logic)

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

Context: `runtime/src/bank.rs:2293` (changes a sensitive control or state-update path)

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

Context: `runtime/src/bank.rs:2305` (changes a sensitive control or state-update path)

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

Context: `core/src/replay_stage.rs:2559` (changes a consensus- or validator-sensitive branch)

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

Move publication of a consensus-observed boundary signal after the state it represents has been fully committed, and block concurrent mutation once freezing begins.

## How It Was Fixed

runtime/src/bank.rs changes Bank::register_tick to use freeze_started(), perform block-boundary blockhash and recent-blockhash sysvar updates before tick_height.fetch_add, and document the dependency with ReplayStage accounts-delta-hash calculation. core/src/replay_stage.rs updates tests to use explicit vote slots and a multi-slot bank chain.

# Why It Matters

1. Consensus depends on validators hashing the same slot state.

2. ReplayStage treats boundary tick height as a signal for freeze/hash work.

3. Publishing that signal too early can race with account-visible slot-finalization updates.

4. Evidence does not show theft, signature bypass, or a concrete attacker-controlled trigger.

# Evidence Notes

The strongest evidence is runtime/src/bank.rs around Bank::register_tick: replacement of is_frozen with freeze_started, movement of tick_height.fetch_add after block-boundary updates, and the added comment tying tick-height observation to ReplayStage accounts delta hash calculation. The replay_stage changes are test-oriented. The provided evidence supports a consensus-safety race but not broader cryptographic failure or a demonstrated exploit path. Protocol security invariant: At a slot boundary, Bank::register_tick must not publish the boundary tick height observed by ReplayStage until blockhash and other account-visible end-of-slot updates are committed, because ReplayStage may use that boundary observation to begin freeze or accounts-delta-hash work. Verification notes: No concrete exploit path is shown by the patch evidence. No evidence shows attacker control over the race timing. No evidence shows funds theft, signature bypass, or unauthorized account mutation. The replay_stage hunks are test-oriented and should not be treated as the runtime vulnerability by themselves. The patch supports consensus-safety relevance, not a broader cryptographic primitive failure. No external exploitability evidence is provided. No attacker timing control is shown. Runtime fix is grounded in Bank::register_tick ordering. ReplayStage hunks should not be classified as the root cause by themselves. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-state-race`
Final tags: `blockchain-core, consensus, validator, replay, race-condition, accounts-hash`

The supplied patch evidence supports retaining this as security hardening in a blockchain consensus/runtime subsystem, but not as a proven security fix. The code reorders tick_height publication so ReplayStage cannot observe a slot boundary before blockhash/sysvar/account-visible updates are committed, and it blocks tick registration once freezing has started. That tightens a consensus-sensitive race condition, but the evidence does not prove attacker control, exploitability, or an actual consensus failure incident.

## Security Evidence

1. runtime/src/bank.rs changes register_tick from guarding only is_frozen() to guarding freeze_started(), preventing mutation during the freeze window.
2. runtime/src/bank.rs moves tick_height.fetch_add until after block-boundary blockhash and recent-blockhash sysvar updates.
3. Added comment states ReplayStage starts accounts delta hash computation after observing boundary tick height, making tick_height an observable consensus-sensitive signal.
4. The changed code is in Solana Bank/replay/freeze logic, a validator consensus-critical path.

## Missing Evidence

1. No demonstrated exploit path or attacker-controlled timing is shown.
2. No evidence shows funds theft, signature bypass, unauthorized account mutation, or cryptographic break.
3. No evidence shows that the race caused a real network consensus failure.
4. ReplayStage hunks appear to be test/support changes rather than direct vulnerable runtime behavior.

## Claim Boundaries

1. Classify as consensus security hardening, not a confirmed exploitable vulnerability.
2. The supported issue is an ordering race around tick publication and accounts hash/freeze work.
3. Do not claim RPC, snapshot, queue, or cryptographic primitive compromise from this evidence.
4. Do not claim concrete malicious exploitability without additional external evidence.
