---
case_id: case_20190620_aacb38864c
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: cryptography
source_quality: high
date: 2019-06-20
source_refs:
  - git:aacb38864cd8ebc4b78e387a91ba71ded5872f78
  - "core/src/replay_stage.rs:274"
  - "core/src/blocktree.rs:858"
  - "core/src/replay_stage.rs:295"
  - "core/src/replay_stage.rs:412"
bug_class: invalid-fork-replay-handling
impact_type:
  - consensus-integrity
  - replay-integrity
confidence: medium
tags:
  - infrastructure
  - consensus
  - replay
  - fork-handling
  - dead-slot
  - validation-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch improves Solana replay-stage dead-fork handling by classifying some replay failures as fatal, marking the affected slot dead, and skipping forks already marked dead in replay progress. The evidence supports consensus-replay correctness and possible security relevance, but it does not establish an exploitable vulnerability, finalized consensus divergence, fund loss, or attacker control.

## Observed Patch Facts

1. In `core/src/replay_stage.rs`, the patch replaces `fn replay_blocktree_into_bank(` with `// Returns Some(result) if the 'result' is a fatal error, which is an error that will...`.

2. In `core/src/blocktree.rs`, the patch replaces `pub fn get_orphans(&self, max: Option<usize>) -> Vec<u64> {` with `pub fn is_dead(&self, slot: u64) -> bool {`.

3. In `core/src/replay_stage.rs`, the patch replaces `let len = entries.len();` with `if Self::is_replay_result_fatal(&result) {`.

4. In `core/src/replay_stage.rs`, the patch replaces `*ticks_per_slot = bank.ticks_per_slot();` with `// If the fork was marked as dead, don't replay it`.

## Project Context

The changed code sits primarily in `core/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `core/src/banking_stage.rs`, `core/src/bank_forks.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `core/src/window_service.rs`, `core/src/tpu.rs`. The strongest project-level identifiers around this patch are `bank`, `result`, `progress`, and `Self::is_replay_result_fatal`.

## Before/After Behavior

Before the change, the shown replay path logged or counted replay failures and included a TODO to mark failed forks, while active banks were replayed without first skipping progress entries marked dead. After the change, fatal replay results trigger mark_dead_slot, active banks with progress.is_dead are skipped, and Blocktree exposes an is_dead(slot) query backed by the DeadSlots column family.

# Root Cause

Fatal replay failures were not shown to be consistently converted into dead-fork state before later replay decisions. The supported root cause is missing or incomplete dead-fork propagation between replay result handling, in-memory fork progress, and Blocktree dead-slot tracking.

## Walkthrough

1. ReplayStage iterates active bank slots from bank_forks in replay_active_banks.

2. The patch adds a check that skips a bank slot when its ForkProgress has is_dead set.

3. replay_blocktree_into_bank loads entries and replays them into the Bank.

4. The patch adds is_replay_result_fatal to classify selected replay errors as fatal.

5. The fatal cases shown are non-committable transaction errors and BlobError::VerificationFailed.

6. When replay_blocktree_into_bank receives a fatal result, it calls mark_dead_slot for the bank slot.

7. Blocktree gains is_dead(slot), which reads the DeadSlots column family.

8. The commit message also says dead forks are filtered from get_slots_since, but the provided hunks do not show that implementation.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/replay_stage.rs | 274 | classifies fatal replay results, including non-committable transaction errors and blob verification failure |
| core/src/replay_stage.rs | 291 | marks the bank slot dead when replaying blocktree entries returns a fatal result |
| core/src/replay_stage.rs | 402 | skips active banks already marked dead in replay progress |
| core/src/blocktree.rs | 858 | queries persisted DeadSlots state from blocktree storage |

## Code Snippets

## Snippet 1

Context: `core/src/replay_stage.rs:274` (changes a sensitive control or state-update path)

Before
```rust
}
    }
    fn replay_blocktree_into_bank(
        bank: &Bank,
```
After
```rust
}
    }

    // Returns Some(result) if the `result` is a fatal error, which is an error that will cause a
    // bank to be marked as dead/corrupted
    fn is_replay_result_fatal(result: &Result<()>) -> bool {
        match result {
            Err(Error::TransactionError(e)) => {
```

## Snippet 2

Context: `core/src/blocktree.rs:858` (changes persisted or aggregate state handling)

Before
```rust
}

    pub fn get_orphans(&self, max: Option<usize>) -> Vec<u64> {
        let mut results = vec![];
```
After
```rust
}

    pub fn is_dead(&self, slot: u64) -> bool {
        if let Some(true) = self
            .db
            .get::<cf::DeadSlots>(slot)
            .expect("fetch from DeadSlots column family failed")
        {
```

## Snippet 3

Context: `core/src/replay_stage.rs:295` (changes signature or replay validation logic)

Before
```rust
) -> Result<()> {
        let (entries, num) = Self::load_blocktree_entries(bank, blocktree, progress)?;
        let len = entries.len();
        let result = Self::replay_entries_into_bank(bank, entries, progress, num);
        if result.is_ok() {
            trace!("verified entries {}", len);
            inc_new_counter_info!("replicate-stage_process_entries", len);
        } else {
```
After
```rust
) -> Result<()> {
        let (entries, num) = Self::load_blocktree_entries(bank, blocktree, progress)?;
        let result = Self::replay_entries_into_bank(bank, entries, progress, num);

        if Self::is_replay_result_fatal(&result) {
            Self::mark_dead_slot(bank.slot(), blocktree, progress);
        }
```

## Snippet 4

Context: `core/src/replay_stage.rs:412` (changes a sensitive control or state-update path)

Before
```rust
for bank_slot in &active_banks {
            let bank = bank_forks.read().unwrap().get(*bank_slot).unwrap().clone();
            *ticks_per_slot = bank.ticks_per_slot();
            if bank.collector_id() != my_pubkey {
                Self::replay_blocktree_into_bank(&bank, &blocktree, progress)?;
            }
            let max_tick_height = (*bank_slot + 1) * bank.ticks_per_slot() - 1;
```
After
```rust
for bank_slot in &active_banks {
            // If the fork was marked as dead, don't replay it
            if progress.get(bank_slot).map(|p| p.is_dead).unwrap_or(false) {
                continue;
            }

            let bank = bank_forks.read().unwrap().get(*bank_slot).unwrap().clone();
```

# Fix Pattern

Detect fatal replay failures, record the affected slot as dead, and avoid replaying slots already marked dead.

## How It Was Fixed

core/src/replay_stage.rs adds fatal replay classification, calls mark_dead_slot after fatal replay results, and skips active banks whose progress is already marked dead. core/src/blocktree.rs adds an is_dead(slot) query for DeadSlots state. The commit message indicates related DeadSlots storage and get_slots_since filtering changes, but those specific code paths are not fully shown in the provided evidence.

# Why It Matters

1. Prevents repeated replay of forks already classified as dead.

2. Treats entry verification failure as a dead/corrupted fork condition.

3. Improves replay and fork-state consistency.

4. Security impact remains unproven from the supplied evidence.

# Evidence Notes

Grounded evidence is in core/src/replay_stage.rs around is_replay_result_fatal, replay_blocktree_into_bank, and replay_active_banks, plus core/src/blocktree.rs is_dead(slot). The evidence does not support the draft's stronger implication of a proven security fix. It also does not support classifying the subsystem as cryptography or the bug class as broad state corruption. Protocol security invariant: Validator replay should exclude slots or forks that have been determined to be dead or corrupted after fatal replay failures such as entry verification failure or non-committable transaction errors. Verification notes: No proof that a remote attacker can reliably trigger the fatal replay paths is shown. No proof of finalized consensus divergence or fund loss is shown by the patch alone. No cryptographic primitive or signature verification algorithm change is shown. The evidence supports invalid/dead fork handling, not a general state-corruption claim across all storage paths. No remote trigger path is shown. No finalized consensus divergence is demonstrated. No fund loss or privilege impact is shown. No cryptographic primitive or signature-verification algorithm change is shown. Regression coverage is mentioned in the commit message but not shown in the supplied hunks. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `invalid-fork-replay-handling`
Final impact type: `consensus-integrity, replay-integrity`
Final confidence: `medium`
Final tags: `infrastructure, consensus, replay, fork-handling, dead-slot, validation-hardening`

The supplied patch evidence supports retaining this as security hardening, not as a proven security fix. The change tightens Solana validator replay behavior by classifying verification and non-committable transaction failures as fatal, marking affected slots dead/corrupted, persisting/querying dead-slot state, and skipping forks already marked dead. That is security-sensitive consensus/replay hardening, but the evidence does not prove exploitability, attacker control, finalized divergence, fund loss, or a cryptographic/signature bug.

## Security Evidence

1. Replay failures from non-committable transaction errors and BlobError::VerificationFailed are explicitly classified as fatal.
2. Fatal replay results cause mark_dead_slot(bank.slot(), blocktree, progress) to run.
3. Replay skips active banks whose progress entry is already marked dead.
4. Blocktree gains an is_dead(slot) query backed by the DeadSlots column family.
5. Commit metadata indicates related filtering of dead forks from get_slots_since and regression testing.

## Missing Evidence

1. No demonstrated remote attacker path to trigger the fatal replay failures.
2. No evidence of finalized consensus divergence before the patch.
3. No proof of fund loss, privilege impact, or chain safety violation.
4. No cryptographic primitive or signature verification algorithm change is shown.
5. Regression test details are mentioned but not included in the supplied hunks.

## Claim Boundaries

1. Treat as consensus replay hardening rather than a confirmed exploitable vulnerability.
2. Do not classify as a cryptography or signature bug from the supplied evidence.
3. Do not claim state corruption beyond invalid/dead fork replay-state handling.
4. Do not claim attacker-controlled exploitation, fund loss, or finalized fork divergence.
