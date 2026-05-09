---
case_id: case_20201215_75e9e321de
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2020-12-15
source_refs:
  - git:75e9e321de9c8b6fcd958a7936de74fc63ebfe3f
  - "core/src/replay_stage.rs:2606"
  - "runtime/src/bank.rs:2293"
  - "runtime/src/bank.rs:2305"
  - "core/src/replay_stage.rs:2559"
bug_class: consensus-state-publication-race
impact_type:
  - consensus-inconsistency
confidence: medium
tags:
  - blockchain-core
  - consensus
  - runtime
  - replay
  - accounts-hash
  - race-condition
  - validator
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes a race in Bank::register_tick where tick_height could be published before boundary-related account updates completed, while ReplayStage uses that boundary tick as a signal to start accounts delta hash calculation. The evidence supports a consensus/account-hash ordering bug, but does not establish remote exploitability, fund theft, signature bypass, or hash forgery.

## Observed Patch Facts

1. In `core/src/replay_stage.rs`, the patch replaces `let bank1 = Bank::new_from_parent(&arc_bank0, &Pubkey::default(), arc_bank0.slot() + 1);` with `for i in 1..=3 {`.

2. In `runtime/src/bank.rs`, the patch replaces `!self.is_frozen(),` with `!self.freeze_started(),`.

3. In `runtime/src/bank.rs`, the patch adds `// ReplayStage will start computing the accounts delta hash when it`.

4. In `core/src/replay_stage.rs`, the patch replaces `fn leader_vote(bank: &Arc<Bank>, pubkey: &Pubkey) {` with `fn leader_vote(vote_slot: Slot, bank: &Arc<Bank>, pubkey: &Pubkey) {`.

## Project Context

The changed code sits primarily in `core/src`, `runtime/src`, which anchors the finding in the `consensus` area of the project. Historical context from `runtime/src/bank_forks.rs`, `core/src/optimistically_confirmed_bank_tracker.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `runtime/src/bank_forks.rs`, `core/src/poh_recorder.rs`. The strongest project-level identifiers around this patch are `bank`, `Bank::new_from_parent`, `Pubkey::default`, and `unwrap`.

## Before/After Behavior

Before the patch, register_tick only rejected fully frozen banks and incremented tick_height before the boundary blockhash/sysvar update sequence, allowing ReplayStage to observe the boundary before all account updates were committed. After the patch, register_tick rejects banks where freezing has started, performs boundary blockhash and recent_blockhashes updates first, and increments tick_height afterward.

# Root Cause

An ordering bug exposed tick_height as a synchronization signal before the state that ReplayStage would hash at that boundary was fully updated. The freeze guard was also weaker than the new invariant because it only checked the completed frozen state.

## Walkthrough

1. Bank::register_tick previously allowed execution while a bank was not yet fully frozen.

2. The old code incremented tick_height before completing the boundary update path shown in the patch context.

3. ReplayStage treats reaching the tick boundary as the point to begin accounts delta hash calculation.

4. The added comment states that all account updates for the slot must be committed before tick_height is incremented.

5. The fix changes the guard from is_frozen to freeze_started.

6. The fix performs blockhash registration and recent_blockhashes sysvar updates before publishing the boundary tick height.

7. Tests in replay_stage were expanded to exercise a multi-bank replay/commitment scenario, but those test changes are supporting evidence rather than the root cause.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| runtime/src/bank.rs | 2293 | Bank::register_tick now rejects ticks after freezing has begun, preventing tick/account-hash state transitions during freeze. |
| runtime/src/bank.rs | 2298 | Boundary blockhash and recent_blockhashes sysvar updates are performed before the tick height boundary is published. |
| runtime/src/bank.rs | 2305 | tick_height.fetch_add is delayed until after account-affecting boundary updates, preserving ReplayStage accounts hash ordering. |
| core/src/replay_stage.rs | 2606 | ReplayStage test coverage now constructs multiple chained banks and ticks to exercise the replay/commitment boundary behavior. |
| core/src/replay_stage.rs | 2559 | Test helper allows voting on explicit slots, supporting the expanded fork/replay scenario. |

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

Move publication of a concurrency-visible boundary signal until after the state it represents has been fully committed, and strengthen the guard against interleaving with freeze processing.

## How It Was Fixed

runtime/src/bank.rs now checks !self.freeze_started(), evaluates whether the next tick reaches a boundary before incrementing tick_height, performs blockhash queue and recent_blockhashes sysvar updates first, then calls tick_height.fetch_add. core/src/replay_stage.rs adds supporting test coverage for chained banks and explicit slot votes.

# Why It Matters

1. Accounts hash calculation is consensus-sensitive.

2. A race in the state used for accounts hashing can create validator-visible inconsistency.

3. The evidence supports consensus-safety relevance, not a specific theft or authorization-bypass scenario.

# Evidence Notes

Grounded evidence comes from runtime/src/bank.rs around Bank::register_tick and the commit subject naming a race between setting tick height and calculating accounts hash. The added comment directly explains the ReplayStage/accounts-delta-hash ordering requirement. Claims beyond consensus/account-hash race impact are unsupported by the supplied evidence. Protocol security invariant: ReplayStage must not observe tick_height at a slot or block boundary until all account-affecting updates for that boundary, including blockhash/recent_blockhashes sysvar updates, have been committed; tick registration must also not interleave with an in-progress bank freeze. Verification notes: No evidence proves a remote attacker can trigger the race on demand. No evidence proves fund theft, signature bypass, or account authorization bypass. No evidence shows cryptographic hash collision or hash forgery. ReplayStage test edits support coverage but are not themselves the security fix. The classification is based on consensus/account-hash ordering, not on general API cleanup. No evidence of remote attacker control was provided. No evidence of fund theft, signature bypass, authorization bypass, hash collision, or hash forgery was provided. ReplayStage test changes support the scenario but are not themselves the vulnerability fix. Confidence is medium because the race and invariant are explicit, while concrete exploitability is not shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-state-publication-race`
Final impact type: `consensus-inconsistency`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, runtime, replay, accounts-hash, race-condition, validator`

The supplied patch evidence supports retaining this as security hardening, not a proven concrete security fix. The change moves publication of tick_height until after boundary account-affecting updates and strengthens the freeze guard, and the added comment explicitly ties this ordering to ReplayStage accounts delta hash calculation. That is security-sensitive consensus behavior, but the evidence does not prove attacker control, exploitability, fund loss, authorization bypass, or an actual observed consensus split.

## Security Evidence

1. Commit subject names a race between setting tick height and calculating accounts hash.
2. runtime/src/bank.rs changes register_tick from checking only is_frozen() to freeze_started(), blocking ticks during in-progress freezing.
3. runtime/src/bank.rs delays tick_height.fetch_add until after blockhash and recent_blockhashes sysvar updates.
4. Added comment states ReplayStage starts accounts delta hash calculation when it observes the boundary tick height and therefore account updates must be committed first.
5. Changed code is in Bank::register_tick and ReplayStage-related tests, which are consensus-sensitive validator/runtime paths.

## Missing Evidence

1. No evidence that a remote attacker can trigger or time the race.
2. No evidence of a demonstrated consensus split, chain halt, or validator divergence.
3. No evidence of fund theft, signature bypass, authorization bypass, or hash forgery.
4. No advisory, CVE, incident report, or exploit scenario is provided in the supplied input.
5. Test changes support the race scenario but do not by themselves prove security exploitability.

## Claim Boundaries

1. Classify as consensus hardening around accounts-hash ordering, not as a proven exploitable vulnerability.
2. Do not claim fund loss, transaction forgery, signature bypass, or cryptographic hash compromise.
3. Do not rely on snapshot, RPC, or queue tags; those are not directly supported by the patch evidence.
4. Keep confidence at medium because the security-sensitive invariant is explicit but concrete exploitability is not shown.
