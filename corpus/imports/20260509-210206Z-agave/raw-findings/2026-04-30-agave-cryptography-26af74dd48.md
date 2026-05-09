---
case_id: case_20260430_26af74dd48
project: agave
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: cryptography
confidence: medium
source_quality: high
date: 2026-04-30
source_refs:
  - git:26af74dd483a6238bfe45932acd399450d71906f
  - "ledger/src/blockstore.rs:10894"
  - "core/benches/shredder.rs:207"
  - "ledger/src/blockstore.rs:1996"
  - "ledger/src/blockstore.rs:1480"
bug_class: consensus-protocol-validation
impact_type:
  - consensus-integrity
  - ledger-integrity
tags:
  - blockchain-core
  - consensus
  - ledger
  - shred-recovery
  - protocol-validation
  - erasure-recovery
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The commit updates Agave's shred recovery path so recovered shreds are handled through a `ShredRecoveryContext` and adds regression coverage for discarding recovered data shreds with unexpected data-complete flags. The evidence supports consensus/ledger validation hardening for recovered shreds, but it does not establish a concrete exploit, signature bypass, or direct validator compromise.

## Observed Patch Facts

1. In `ledger/src/blockstore.rs`, the patch replaces `fn test_index_integrity() {` with `fn test_recovery_discards_unexpected_data_complete_shreds() {`.

2. In `core/benches/shredder.rs`, the patch replaces `for shred in recover(coding_shreds.clone(), &reed_solomon_cache).unwrap() {` with `let mut shred_recovery_context = new_shred_recovery_context(&coding_shreds);`.

3. In `ledger/src/blockstore.rs`, the patch replaces `if let Some((reed_solomon_cache, retransmit_sender)) = should_recover_shreds {` with `if let Some(shred_recovery_context) = shred_recovery_context {`.

4. In `ledger/src/blockstore.rs`, the patch replaces `fn try_shred_recovery<'a>(` with `/// Attempt shred recovery for erasure metas`.

## Project Context

The changed code sits primarily in `ledger/src`, `core/benches`, which anchors the finding in the `cryptography` area of the project. Historical context from `ledger/src/sigverify_shreds.rs`, `ledger/src/shredder.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/shredder.rs`, `ledger/src/shred.rs`. The strongest project-level identifiers around this patch are `Vec::new`, `shred_recovery_context`, `shreds`, and `reed_solomon_cache`.

## Before/After Behavior

Before the change, the supplied evidence shows recovery using raw Reed-Solomon recovery plumbing such as `recover(coding_shreds.clone(), &reed_solomon_cache).unwrap()` in the benchmark and `Some((reed_solomon_cache, retransmit_sender))` in blockstore insertion. After the change, recovery is routed through `ShredRecoveryContext`, with recovered shred buffers passed into context-aware recovery. A new regression test activates `discard_unexpected_data_complete_shreds` and checks that recovered shreds with unexpected data-complete metadata are discarded.

# Root Cause

Recovered shreds appear to have had a separate recovery path where the provided evidence does not show the newly required SIMD-0337 validity rule being applied. The grounded case is recovered data shreds carrying unexpected data-complete flags.

## Walkthrough

1. Coding shreds enter blockstore insertion and may be eligible for erasure recovery.

2. The old interface exposed recovery through Reed-Solomon cache and retransmit sender plumbing.

3. The patch changes blockstore insertion and benchmarks to use `ShredRecoveryContext`.

4. The recovery comments document eligibility checks around new shreds, erasure-set existence, and sufficient shard counts.

5. The new regression test activates `discard_unexpected_data_complete_shreds`.

6. The fixed behavior evidenced by the test is that recovered data shreds with unexpected data-complete flags are discarded.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| ledger/src/blockstore.rs | 1480 | Defines shred recovery rules and decides which erasure sets are eligible for recovered shred generation. |
| ledger/src/blockstore.rs | 1963 | Inserts received shreds and then routes eligible recovery through `ShredRecoveryContext` before recovered shreds affect blockstore state or retransmission. |
| ledger/src/blockstore.rs | 10894 | Adds regression coverage that recovered shreds with unexpected data-complete flags are discarded under the new feature. |
| core/benches/shredder.rs | 207 | Updates benchmark recovery path to use `ShredRecoveryContext`, reflecting the new validated recovery API rather than raw erasure recovery. |
| feature-set/src/lib.rs | 0 | Adds or wires the feature gate for discarding unexpected data-complete shreds. |
| ledger/src/shred/filter.rs | 0 | Likely contains the shred-level filtering logic used to apply SIMD-0337 rules to recovered shreds. |
| ledger/src/shred/merkle.rs | 0 | Part of shred construction/verification surface touched by the rule update, based on the changed file list. |

## Code Snippets

## Snippet 1

Context: `ledger/src/blockstore.rs:10894` (changes signature or replay validation logic)

Before
```rust
}

    #[test]
    fn test_index_integrity() {
```
After
```rust
}

    #[test]
    fn test_recovery_discards_unexpected_data_complete_shreds() {
        const DATA_SHRED_FLAGS_OFFSET: usize = 85;

        let ledger_path = get_tmp_ledger_path_auto_delete!();
        let blockstore = Blockstore::open(ledger_path.path()).unwrap();
```

## Snippet 2

Context: `core/benches/shredder.rs:207` (changes the branch that decides whether execution stops or continues)

Before
```rust
.partition(Shred::is_data);
    coding_shreds.truncate(CODING_SHREDS_PER_FEC_BLOCK);

    bencher.iter(|| {
        for shred in recover(coding_shreds.clone(), &reed_solomon_cache).unwrap() {
            black_box(shred.unwrap());
        }
    })
```
After
```rust
.partition(Shred::is_data);
    coding_shreds.truncate(CODING_SHREDS_PER_FEC_BLOCK);
    let mut shred_recovery_context = new_shred_recovery_context(&coding_shreds);

    bencher.iter(|| {
        let mut recovered_shreds = Vec::new();
        let mut recovered_data_shreds = Vec::new();
        shred_recovery_context
```

## Snippet 3

Context: `ledger/src/blockstore.rs:1996` (changes a sensitive control or state-update path)

Before
```rust
metrics,
        );
        if let Some((reed_solomon_cache, retransmit_sender)) = should_recover_shreds {
            self.handle_shred_recovery(
                leader_schedule,
                reed_solomon_cache,
                &mut shred_insertion_tracker,
                retransmit_sender,
```
After
```rust
metrics,
        );
        if let Some(shred_recovery_context) = shred_recovery_context {
            self.handle_shred_recovery(
                leader_schedule,
                shred_recovery_context,
                &mut shred_insertion_tracker,
                is_trusted,
```

## Snippet 4

Context: `ledger/src/blockstore.rs:1480` (changes a sensitive control or state-update path)

Before
```rust
}

    fn try_shred_recovery<'a>(
        &'a self,
        erasure_metas: &'a BTreeMap<ErasureSetId, WorkingEntry<ErasureMeta>>,
        index_working_set: &'a HashMap<(BlockLocation, u64), IndexMetaWorkingSetEntry>,
        prev_inserted_shreds: &'a HashMap<(BlockLocation, ShredId), Cow<'_, Shred>>,
        reed_solomon_cache: &'a ReedSolomonCache,
```
After
```rust
}

    /// Attempt shred recovery for erasure metas
    /// Recovery rules:
    /// 1. Only try recovery around indexes for which new data or coding shreds are received
    /// 2. For new data shreds, check if an erasure set exists. If not, don't try recovery
    /// 3. Before trying recovery, check if enough number of shreds have been received
    ///    3a. Enough number of shreds = (#data + #coding shreds) > erasure.num_data
```

# Fix Pattern

Route recovered shreds through protocol-aware recovery handling and add a regression test for the feature-gated discard rule.

## How It Was Fixed

`do_insert_shreds` now accepts an optional `ShredRecoveryContext` and passes it to recovery handling instead of passing only raw Reed-Solomon recovery inputs. The shredder benchmark was updated to exercise the context-based recovery API. Regression coverage was added for discarding recovered data shreds with unexpected data-complete flags when `discard_unexpected_data_complete_shreds` is active. The changed file list includes feature and shred filter files, but the exact filter implementation is not shown in the provided excerpts.

# Why It Matters

1. Recovered shreds can enter ledger recovery through a different path than directly received shreds.

2. Consensus-sensitive metadata should be validated consistently across recovery paths.

3. The evidenced issue is unexpected data-complete metadata on recovered shreds.

4. The evidence does not prove a signature bypass or forged transaction execution.

# Evidence Notes

Strong evidence comes from `ledger/src/blockstore.rs` adding `test_recovery_discards_unexpected_data_complete_shreds`, the shift from `(reed_solomon_cache, retransmit_sender)` to `ShredRecoveryContext`, and the benchmark replacing raw `recover(...)` usage with context-based recovery. The commit subject supports the SIMD-0337 framing. Unsupported or unproven claims include remote exploitability, validator compromise, signature verification bypass, direct transaction execution impact, and the full details of every SIMD-0337 rule beyond unexpected data-complete shred handling. Protocol security invariant: Erasure-recovered shreds should be checked against the applicable SIMD-0337 shred validity rules before being treated as valid recovered ledger data. The specifically evidenced rule is discarding recovered data shreds with unexpected data-complete flags when the corresponding feature is active. Verification notes: The evidence does not prove signature verification was bypassed. The evidence does not prove remote exploitability or validator compromise. The evidence does not show transaction execution or account state mutation directly accepting forged data. The evidence supports a recovered-shred protocol validation gap, not a broad cryptography bug. The exact SIMD-0337 rule details beyond unexpected data-complete shred handling are not fully shown in the provided patch excerpts. No external inspection was performed; assessment is limited to the supplied excerpts. The finding is classified as likely security hardening, not a confirmed vulnerability fix. Confidence is medium because the specific regression is clear, but the full implementation and exploitability are not shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `consensus-protocol-validation`
Final impact type: `consensus-integrity, ledger-integrity`
Final tags: `blockchain-core, consensus, ledger, shred-recovery, protocol-validation, erasure-recovery`

The supplied evidence supports keeping this as security hardening: recovered shreds are moved onto a context-aware recovery path and a regression test verifies that recovered data shreds with unexpected data-complete flags are discarded under the relevant feature. This is security-sensitive consensus and ledger validation behavior, but the excerpts do not prove a concrete exploit, replay attack, signature bypass, or direct validator compromise. The original cryptography/replay/signature framing is too specific for the shown evidence.

## Security Evidence

1. Commit subject explicitly says SIMD-0337 rules are applied to recovered shreds.
2. New test `test_recovery_discards_unexpected_data_complete_shreds` activates `discard_unexpected_data_complete_shreds` and covers discard behavior for recovered shreds.
3. Blockstore insertion now passes a `ShredRecoveryContext` into recovery handling instead of raw Reed-Solomon recovery inputs.
4. The affected path handles ledger shred recovery, which is consensus-sensitive protocol data handling.

## Missing Evidence

1. No excerpt shows a signature verification bypass.
2. No exploit scenario or attacker-controlled replay path is demonstrated.
3. No direct evidence of transaction execution or account-state corruption from the old behavior is supplied.
4. The exact SIMD-0337 filtering implementation is not shown in the provided evidence.

## Claim Boundaries

1. Classify as security hardening, not a proven vulnerability fix.
2. Limit the validated issue to recovered-shred protocol validation.
3. Do not claim request forgery, replay, or signature-validation failure from the supplied patch alone.
4. Do not infer remote exploitability or validator compromise.
