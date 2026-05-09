---
case_id: case_20201113_f6b65b033e
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
confidence: medium
source_quality: high
date: 2020-11-13
source_refs:
  - git:f6b65b033eaa09d484c1581459d897d2fe12996f
  - "ledger/src/entry.rs:901"
  - "ledger/src/entry.rs:623"
bug_class: arithmetic-overflow-in-validation-counter
impact_type:
  - validation-integrity
tags:
  - blockchain-core
  - ledger-validation
  - tick-verification
  - arithmetic-overflow
  - proof-of-history
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes overflow-sensitive arithmetic in `ledger/src/entry.rs` during tick hash count verification. The running `tick_hash_count` previously used direct `u64` addition and now uses `saturating_add`, so oversized cumulative counts cannot wrap before the exact equality check against `hashes_per_tick`.

## Observed Patch Facts

1. In `ledger/src/entry.rs`, the patch replaces `let tx_entry = Entry::new(&Hash::default(), 1, vec![tx]);` with `let no_hash_tx_entry = Entry {`.

2. In `ledger/src/entry.rs`, the patch replaces `*tick_hash_count += entry.num_hashes;` with `*tick_hash_count = tick_hash_count.saturating_add(entry.num_hashes);`.

## Project Context

The changed code sits primarily in `ledger/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `ledger/src/shred.rs`, `ledger/src/rooted_slot_iterator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/shred.rs`, `ledger/src/rooted_slot_iterator.rs`. The strongest project-level identifiers around this patch are `Hash::default`, `Entry::new_tick`, `Entry`, and `default`.

## Before/After Behavior

Before the change, `verify_tick_hash_count` accumulated `entry.num_hashes` with `*tick_hash_count += entry.num_hashes` and then compared the result to `hashes_per_tick` at tick entries. After the change, accumulation uses `tick_hash_count.saturating_add(entry.num_hashes)`, preserving an overlarge value instead of allowing wraparound. Tests were adjusted to construct entries with explicit transaction and hash-count fields for edge-case coverage.

# Root Cause

The verifier used overflow-sensitive arithmetic for a validation counter whose value determines whether a tick hash count is accepted or rejected.

## Walkthrough

1. `verify_tick_hash_count` receives entries, a mutable running `tick_hash_count`, and `hashes_per_tick`.

2. When `hashes_per_tick` is nonzero, each entry contributes `entry.num_hashes` to the running count.

3. Before the patch, the counter was updated with direct `u64` addition.

4. At tick entries, the accumulated count is compared with `hashes_per_tick`; mismatches are rejected.

5. If accumulation overflowed, the verifier could make that comparison using a wrapped value rather than the true cumulative count.

6. The patch changes the update to `saturating_add`, so overflowed totals remain too large for an exact match rather than wrapping.

7. The test setup was revised to exercise controlled zero, one, partial, and tick hash-count cases.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| ledger/src/entry.rs | 618 | Implements `verify_tick_hash_count`, the ledger entry validation routine enforcing per-tick hash count consistency. |
| ledger/src/entry.rs | 623 | Changed accumulation of `tick_hash_count` from unchecked addition to saturating addition to avoid overflow/wraparound during verification. |
| ledger/src/entry.rs | 900 | Regression test coverage for tick hash count verification edge cases using explicitly constructed entries. |

## Code Snippets

## Snippet 1

Context: `ledger/src/entry.rs:901` (changes signature or replay validation logic)

Before
```rust
let hashes_per_tick = 10;
        let tx = Transaction::default();
        let tx_entry = Entry::new(&Hash::default(), 1, vec![tx]);
        let full_tick_entry = Entry::new_tick(hashes_per_tick, &Hash::default());
        let partial_tick_entry = Entry::new_tick(hashes_per_tick - 1, &Hash::default());
        let no_hash_tick_entry = Entry::new_tick(0, &Hash::default());
        let single_hash_tick_entry = Entry::new_tick(1, &Hash::default());
```
After
```rust
let hashes_per_tick = 10;
        let tx = Transaction::default();

        let no_hash_tx_entry = Entry {
            transactions: vec![tx.clone()],
            ..Entry::default()
        };
        let single_hash_tx_entry = Entry {
```

## Snippet 2

Context: `ledger/src/entry.rs:623` (changes a sensitive control or state-update path)

Before
```rust
for entry in self {
            *tick_hash_count += entry.num_hashes;
            if entry.is_tick() {
                if *tick_hash_count != hashes_per_tick {
```
After
```rust
for entry in self {
            *tick_hash_count = tick_hash_count.saturating_add(entry.num_hashes);
            if entry.is_tick() {
                if *tick_hash_count != hashes_per_tick {
```

# Fix Pattern

Use overflow-safe arithmetic for validation counters that enforce protocol invariants.

## How It Was Fixed

`ledger/src/entry.rs` changed the tick hash count update from direct addition to `saturating_add`. The associated test was updated to build entries explicitly with controlled `num_hashes` and transaction contents.

# Why It Matters

1. Ledger entry verification depends on exact PoH tick hash counts.

2. Overflow in the accumulator can affect validation behavior.

3. The fix is localized to entry tick hash count verification.

4. The supplied evidence does not prove remote exploitability or a consensus split.

# Evidence Notes

The strongest evidence is the focused change at `ledger/src/entry.rs` line 623 replacing `*tick_hash_count += entry.num_hashes` with `*tick_hash_count = tick_hash_count.saturating_add(entry.num_hashes)`. The commit message explicitly describes an overflow fix in entry hash/tick count verification. The related test changes support edge-case validation coverage. Broader claims about shred, blockstore, rooted-slot iteration, transaction execution compromise, remote exploitability, forged ledger acceptance, or consensus failure are not established by the provided evidence. Protocol security invariant: Ledger entry tick verification must compute the cumulative `num_hashes` between tick entries without arithmetic wraparound before checking that the count exactly equals `hashes_per_tick`. Verification notes: Remote exploitability is not proven by the patch evidence. A consensus split or accepted forged ledger is not directly demonstrated. The exact pre-patch runtime behavior under release overflow settings is not proven here. No broader shred, blockstore, or rooted-slot iterator vulnerability is shown by the changed lines. The patch proves overflow-sensitive validation behavior, not transaction execution compromise. Confirmed by provided diff evidence only; no commands or external context were used. Security relevance is likely because the changed arithmetic feeds ledger tick hash count validation. Confidence is medium because the exact exploit path and pre-patch runtime overflow behavior are not demonstrated in the supplied input. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `arithmetic-overflow-in-validation-counter`
Final impact type: `validation-integrity`
Final tags: `blockchain-core, ledger-validation, tick-verification, arithmetic-overflow, proof-of-history`

The supplied patch clearly changes overflow-sensitive arithmetic in a ledger entry tick hash count verifier from direct addition to saturating addition. That is security-relevant hardening because the counter feeds an exact validation check for a protocol invariant. However, the evidence does not prove a concrete exploitable vulnerability, remote attack path, consensus split, or liveness failure, so the finding should be retained as security-hardening rather than a confirmed security-fix.

## Security Evidence

1. Commit message explicitly says it fixes overflow in entry tick/hash count verification.
2. Runtime validation code changes `*tick_hash_count += entry.num_hashes` to `saturating_add`.
3. The changed value is immediately compared against `hashes_per_tick` to accept or reject tick hash counts.
4. The touched code is in blockchain ledger entry verification, a security-sensitive protocol validation path.

## Missing Evidence

1. No supplied proof that an attacker can control `entry.num_hashes` in this path.
2. No supplied regression case showing a wrapped value was previously accepted as valid.
3. No demonstrated consensus split, forged ledger acceptance, or denial-of-service impact.
4. No evidence tying the related shred, blockstore, or iterator context to the overflow fix.

## Claim Boundaries

1. Classify as overflow-safe validation hardening, not a proven exploit fix.
2. Do not claim transaction execution compromise or database corruption from this patch.
3. Do not claim remote exploitability from the supplied evidence alone.
4. Do not keep the original liveness-failure/database framing because the patch only proves arithmetic hardening in ledger tick verification.
