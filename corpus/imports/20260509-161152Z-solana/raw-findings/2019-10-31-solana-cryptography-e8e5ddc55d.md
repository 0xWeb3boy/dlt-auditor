---
case_id: case_20191031_e8e5ddc55d
project: solana
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2019-10-31
source_refs:
  - git:e8e5ddc55d20c57eec659da10c3f106cffef2f25
  - "core/src/replay_stage.rs:762"
  - "ledger/src/blocktree_processor.rs:296"
  - "core/src/replay_stage.rs:815"
  - "ledger/src/blocktree_processor.rs:351"
bug_class: consensus-ledger-validation
impact_type:
  - ledger-integrity
  - consensus-integrity
tags:
  - infrastructure
  - consensus
  - ledger-validation
  - proof-of-history
  - replay
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit PoH/tick validation in Solana replay and blocktree processing paths. The strongest grounded claim is that replayed or loaded entries were missing explicit checks for tick hash counts and slot tick counts in the shown paths, and the patch rejects mismatches with typed block errors. The evidence supports a consensus/ledger-integrity hardening or likely security fix, but not a proven exploit or demonstrated network-level compromise.

## Observed Patch Facts

1. In `core/src/replay_stage.rs`, the patch replaces `fn verify_and_process_entries(` with `fn verify_ticks(`.

2. In `ledger/src/blocktree_processor.rs`, the patch replaces `if opts.verify_ledger && !entries.verify(&last_entry_hash) {` with `if opts.verify_ledger {`.

3. In `core/src/replay_stage.rs`, the patch replaces `return Err(Error::BlobError(BlobError::VerificationFailed));` with `Err(Error::BlockError(block_error))`.

4. In `ledger/src/blocktree_processor.rs`, the patch replaces `BlocktreeProcessorError::LedgerVerificationFailed` with `BlocktreeProcessorError::FailedToLoadEntries`.

## Project Context

The changed code sits primarily in `core/src`, `ledger/src`, which anchors the finding in the `cryptography` area of the project. Historical context from `ledger/src/bank_forks.rs`, `core/src/banking_stage.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/bank_forks.rs`, `core/src/window_service.rs`. The strongest project-level identifiers around this patch are `entries`, `BlocktreeProcessorError::LedgerVerificationFailed`, `bank`, and `slot`.

## Before/After Behavior

Before the patch, the shown replay path entered entry verification and processing without the new standalone `verify_tick_hash_count` check, and the shown blocktree processor ledger verification was tied to `entries.verify(&last_entry_hash)`. After the patch, replay calls `ReplayStage::verify_ticks` before normal processing and rejects `InvalidTickHashCount`; verified blocktree processing checks that `bank.tick_height() + entries.tick_count()` equals `bank.max_tick_height()` and rejects `InvalidTickCount`; bank0 processing is routed through the common slot-entry verification path before freeze.

# Root Cause

The supported root cause is incomplete validation of PoH tick structure in ledger replay/blocktree processing paths. The evidence does not support broader claims such as memory corruption, signature verification bypass, fund loss, double spend, validator takeover, or proven remote exploitability.

## Walkthrough

1. Replay receives a batch of `Entry` values and calls `verify_and_process_entries`.

2. The patch adds `ReplayStage::verify_ticks`, which gets `hashes_per_tick` from the bank and calls `entries.verify_tick_hash_count`.

3. If that check fails, replay now returns `BlockError::InvalidTickHashCount` through the block-error handling path.

4. The blocktree processor now checks, when ledger verification is enabled, whether the entries' tick count brings the bank to `max_tick_height`.

5. If the slot tick count is unexpected, processing returns `BlockError::InvalidTickCount`.

6. Bank0 processing now uses the shared slot-entry verification function before freezing the bank.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| core/src/replay_stage.rs | 762 | Adds verify_ticks to validate entries.verify_tick_hash_count against bank.hashes_per_tick before replay processing continues. |
| core/src/replay_stage.rs | 815 | Calls verify_ticks from verify_and_process_entries and converts tick validation failures into BlockError replay failures. |
| ledger/src/blocktree_processor.rs | 296 | Adds slot-level tick-count validation so verified ledger processing rejects slots whose entry tick count does not reach bank.max_tick_height. |
| ledger/src/blocktree_processor.rs | 351 | Routes bank0 processing through verify_and_process_slot_entries, applying the common ledger verification path before freeze. |

## Code Snippets

## Snippet 1

Context: `core/src/replay_stage.rs:762` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    fn verify_and_process_entries(
        bank: &Arc<Bank>,
```
After
```rust
}

    fn verify_ticks(
        bank: &Arc<Bank>,
        entries: &[Entry],
        tick_hash_count: &mut u64,
    ) -> std::result::Result<(), BlockError> {
        if entries.is_empty() {
```

## Snippet 2

Context: `ledger/src/blocktree_processor.rs:296` (changes signature or replay validation logic)

Before
```rust
assert!(!entries.is_empty());

    if opts.verify_ledger && !entries.verify(&last_entry_hash) {
        warn!("Ledger proof of history failed at slot: {}", bank.slot());
        return Err(BlocktreeProcessorError::LedgerVerificationFailed);
    }
```
After
```rust
assert!(!entries.is_empty());

    if opts.verify_ledger {
        let next_bank_tick_height = bank.tick_height() + entries.tick_count();
        let max_bank_tick_height = bank.max_tick_height();
        if next_bank_tick_height != max_bank_tick_height {
            warn!(
                "Invalid number of entry ticks found in slot: {}",
```

## Snippet 3

Context: `core/src/replay_stage.rs:815` (changes signature or replay validation logic)

Before
```rust
("last_entry", last_entry.to_string(), String),
            );
            return Err(Error::BlobError(BlobError::VerificationFailed));
        }
        verify_total.stop();
        bank_progress.stats.entry_verification_elapsed =
```
After
```rust
("last_entry", last_entry.to_string(), String),
            );

            Err(Error::BlockError(block_error))
        };

        if let Err(block_error) = Self::verify_ticks(bank, entries, tick_hash_count) {
            return handle_block_error(block_error);
```

## Snippet 4

Context: `ledger/src/blocktree_processor.rs:351` (changes a sensitive control or state-update path)

Before
```rust
let entries = blocktree.get_slot_entries(0, 0, None).map_err(|err| {
        warn!("Failed to load entries for slot 0, err: {:?}", err);
        BlocktreeProcessorError::LedgerVerificationFailed
    })?;

    if entries.is_empty() {
        warn!("entry0 not present");
        return Err(BlocktreeProcessorError::LedgerVerificationFailed);
```
After
```rust
let entries = blocktree.get_slot_entries(0, 0, None).map_err(|err| {
        warn!("Failed to load entries for slot 0, err: {:?}", err);
        BlocktreeProcessorError::FailedToLoadEntries
    })?;

    verify_and_process_slot_entries(bank0, &entries, bank0.last_blockhash(), opts)?;

    bank0.freeze();
```

# Fix Pattern

Add explicit pre-processing validation for PoH/tick invariants and reject mismatches through typed ledger/block errors before replay processing or bank freeze continues.

## How It Was Fixed

The patch introduced `verify_ticks` in replay, called it near the start of `verify_and_process_entries`, converted failures to `Error::BlockError`, added a slot-level tick-count check in `verify_and_process_slot_entries`, and routed bank0 through that common verification path.

# Why It Matters

1. Malformed PoH tick structure is rejected earlier in replay.

2. Verified ledger processing now checks the expected slot tick count.

3. The fix strengthens consensus-critical ledger validation paths.

4. The evidence does not establish practical exploitability.

# Evidence Notes

Primary evidence comes from `core/src/replay_stage.rs` adding `verify_ticks` and calling it from `verify_and_process_entries`, plus `ledger/src/blocktree_processor.rs` adding the tick-count check and routing bank0 through `verify_and_process_slot_entries`. The commit subject and body describe verifying hash counts and fixing a tick check. The provided evidence is sufficient for likely security relevance in consensus/ledger validation, but insufficient for a confirmed vulnerability claim. Protocol security invariant: Replayed or loaded ledger entries should match the bank's Proof-of-History tick schedule before they are processed or the bank is frozen: per-tick hash counts must match the bank's hashes_per_tick setting, and the slot's tick count must reach the bank's expected max tick height. Verification notes: The patch does not prove remote exploitability. The patch does not prove malformed entries could be finalized by the network. The patch does not show signature verification bypass. The patch does not demonstrate fund loss, double spend, or validator takeover. The evidence supports consensus/ledger validation impact, not a memory-safety issue. Downgraded mapper verdict from confirmed to likely because exploitability and prior acceptance consequences are not shown. Downgraded confidence from high to medium because the evidence shows added validation but not the full pre-patch semantics of `entries.verify`. Kept in security corpus because the changed checks enforce consensus-relevant PoH/tick invariants in replay and ledger processing. Removed unsupported claims about state corruption, cryptographic key paths, fund loss, finalization, or validator compromise. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-ledger-validation`
Final impact type: `ledger-integrity, consensus-integrity`
Final tags: `infrastructure, consensus, ledger-validation, proof-of-history, replay, state-integrity`

The supplied patch evidence supports retaining this as security hardening: it adds explicit PoH/tick invariant checks in replay and blocktree processing, rejects invalid tick hash counts or slot tick counts, and routes bank0 through common slot-entry verification before freeze. The evidence does not prove exploitability, fund loss, signature bypass, or concrete state corruption, so the original state-corruption and signature/snapshot framing should be narrowed.

## Security Evidence

1. Replay adds verify_ticks and rejects entries that fail verify_tick_hash_count with InvalidTickHashCount.
2. Blocktree processor checks that entry tick count reaches bank.max_tick_height during verified ledger processing.
3. Bank0 processing is routed through verify_and_process_slot_entries before freeze.
4. The touched paths are replay and ledger/blocktree processing, which are consensus and ledger-integrity sensitive.

## Missing Evidence

1. No exploit scenario or adversarial input path is demonstrated.
2. No evidence that malformed entries could be finalized or accepted by the network before the patch.
3. No evidence of signature verification bypass, fund loss, double spend, or validator takeover.
4. No full pre-patch semantics of entries.verify are provided, limiting certainty about the exact prior validation gap.

## Claim Boundaries

1. Classify as security hardening, not a confirmed vulnerability fix.
2. Limit impact to consensus/ledger integrity validation.
3. Do not claim memory corruption, cryptographic key compromise, signature bypass, or snapshot-specific impact.
4. Do not claim proven state corruption or practical exploitability from the supplied patch alone.
