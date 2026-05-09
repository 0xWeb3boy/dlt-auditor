---
case_id: case_20201113_5a61827702
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
  - git:5a61827702bf64d7bbcb50a5a6e2b699fb646f61
  - "ledger/src/entry.rs:899"
  - "ledger/src/entry.rs:623"
bug_class: integer-overflow
impact_type:
  - validation-integrity
tags:
  - blockchain-core
  - ledger-validation
  - proof-of-history
  - integer-overflow
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch fixes overflow-prone arithmetic in Solana ledger entry tick hash verification. `verify_tick_hash_count` previously added each `entry.num_hashes` into a `u64` accumulator with `+=` before checking tick boundaries. The fix uses `saturating_add`, so excessive cumulative hash counts remain excessive instead of wrapping to a smaller value.

## Observed Patch Facts

1. In `ledger/src/entry.rs`, the patch replaces `let tx_entry = Entry::new(&Hash::default(), 1, vec![tx]);` with `let no_hash_tx_entry = Entry {`.

2. In `ledger/src/entry.rs`, the patch replaces `*tick_hash_count += entry.num_hashes;` with `*tick_hash_count = tick_hash_count.saturating_add(entry.num_hashes);`.

## Project Context

The changed code sits primarily in `ledger/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `ledger/src/shred.rs`, `ledger/src/rooted_slot_iterator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `ledger/src/shred.rs`, `ledger/src/rooted_slot_iterator.rs`. The strongest project-level identifiers around this patch are `Hash::default`, `Entry::new_tick`, `Entry`, and `default`.

## Before/After Behavior

Before the patch, `verify_tick_hash_count` skipped verification when `hashes_per_tick == 0`, then accumulated `entry.num_hashes` with unchecked `u64` addition and compared the accumulator to `hashes_per_tick` at tick entries. After the patch, the control flow and tick comparison remain the same, but accumulation uses `saturating_add`, preventing wraparound during validation. The tests were adjusted to construct transaction entries with explicit `num_hashes` values for edge-case coverage.

# Root Cause

The root cause was overflow-prone accumulator arithmetic in a ledger validation routine. Because the validation decision depended on the accumulated hash count, wrapping could make the checked value differ from the true cumulative count.

## Walkthrough

1. `verify_tick_hash_count` receives a mutable `tick_hash_count` accumulator and an expected `hashes_per_tick` value.

2. If `hashes_per_tick` is zero, the function returns true because hashing is treated as disabled.

3. Otherwise, the function iterates through ledger entries and accumulates each `entry.num_hashes`.

4. Before the fix, accumulation used `*tick_hash_count += entry.num_hashes`, which could overflow the `u64` accumulator.

5. At tick entries, the function checks whether the accumulated count equals `hashes_per_tick`.

6. If overflow occurred before that comparison, the comparison would use a wrapped value rather than the true cumulative count.

7. The patch replaces the addition with `tick_hash_count.saturating_add(entry.num_hashes)`, so an excessive count cannot wrap into a smaller value.

8. The test setup was revised to create transaction entries with explicit hash-count fields, including no-hash and single-hash cases.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| ledger/src/entry.rs | 618 | `verify_tick_hash_count` validates cumulative hashes between tick entries against the expected `hashes_per_tick` value. |
| ledger/src/entry.rs | 623 | Changed accumulation of `entry.num_hashes` from unchecked addition to saturating addition to avoid overflow during verification. |
| ledger/src/entry.rs | 898 | Test coverage was adjusted around tick and transaction entries used to exercise hash-count verification edge cases. |

## Code Snippets

## Snippet 1

Context: `ledger/src/entry.rs:899` (changes signature or replay validation logic)

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

Use saturating arithmetic for validation accumulators where later checks depend on monotonic cumulative counts.

## How It Was Fixed

In `ledger/src/entry.rs`, inside `verify_tick_hash_count`, the accumulator update changed from `*tick_hash_count += entry.num_hashes;` to `*tick_hash_count = tick_hash_count.saturating_add(entry.num_hashes);`. Related tests in `test_verify_tick_hash_count` were updated to use explicit `Entry` construction for controlled `num_hashes` cases.

# Why It Matters

1. Ledger entry verification depends on exact PoH hash-count accounting.

2. Overflow can invalidate an equality-based validation check.

3. Saturating addition preserves an over-limit state instead of allowing wraparound.

4. The evidence supports a validation-path security fix, but not confirmed practical exploitability.

# Evidence Notes

Primary evidence is limited to `ledger/src/entry.rs`. The implementation change is the replacement of unchecked accumulator addition with `saturating_add` in `verify_tick_hash_count` around line 623. The surrounding code compares the accumulated count to `hashes_per_tick` when `entry.is_tick()` is true and returns true when `hashes_per_tick == 0`. Test evidence around line 898 shows explicit construction of entries with controlled `num_hashes`. The supplied evidence does not establish remote exploitability, validator crash, consensus divergence, or changes outside the entry verification path. Protocol security invariant: Ledger entry tick verification must compare the true cumulative Proof-of-History hash count between tick entries against `hashes_per_tick`; arithmetic used to compute that count must not wrap before the equality check. Verification notes: The patch does not prove that a remote attacker could submit such entries successfully. The patch does not prove validator crash or consensus divergence in all build configurations. The patch does not show changes to shred networking, storage, or fork-choice logic beyond the entry verification path. The patch does not establish that malformed overflowed entries were accepted in every runtime scenario. Grounded by a focused implementation change in `verify_tick_hash_count`. Commit message explicitly identifies an overflow fix in entry tick/hash count verification. Security impact is likely because the overflow is in ledger validation logic. Confidence is medium because the provided evidence does not show the full ingestion or exploit path. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow`
Final impact type: `validation-integrity`
Final tags: `blockchain-core, ledger-validation, proof-of-history, integer-overflow, security-hardening`

The supplied evidence supports retaining this as security hardening, not a confirmed security fix. The patch replaces unchecked u64 accumulator addition with saturating_add inside ledger entry tick hash verification, a consensus/ledger validation path where wraparound could undermine an equality-based validation check. However, the evidence does not prove exploitability, remote reachability, validator crash, consensus divergence, or that malformed entries were actually accepted in practice.

## Security Evidence

1. Commit message explicitly identifies an overflow fix in entry tick/hash count verification.
2. Runtime validation code changed from unchecked accumulator addition to saturating arithmetic.
3. The affected function verifies cumulative hash counts against hashes_per_tick for ledger entries.
4. The changed code is in Solana ledger/Proof-of-History-related validation logic, which is security-sensitive in a blockchain core.

## Missing Evidence

1. No demonstrated exploit path or attacker-controlled input flow is provided.
2. No evidence shows malformed overflowed entries were accepted by validators before the patch.
3. No evidence establishes consensus divergence, chain integrity compromise, or validator denial of service.
4. Only a focused arithmetic change and tests are shown; surrounding ingestion and enforcement behavior is not proven.

## Claim Boundaries

1. Classify as security-hardening because the patch tightens validation arithmetic in a sensitive path.
2. Do not claim confirmed practical exploitability from the supplied evidence alone.
3. Do not retain the original liveness-failure framing as the primary bug class; integer overflow in validation is better supported.
4. Do not claim a concrete consensus or remote attack impact without additional evidence.
