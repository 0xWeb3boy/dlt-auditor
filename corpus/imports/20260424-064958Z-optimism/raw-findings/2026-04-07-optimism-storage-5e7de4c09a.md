---
case_id: case_20260407_5e7de4c09a
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: storage
impact_type:
  - state-integrity
confidence: low
source_quality: high
date: 2026-04-07
source_refs:
  - git:5e7de4c09a9bdb917b6c1c10622e9bd036a6b9c1
  - "rust/op-reth/crates/trie/src/db/store.rs:676"
  - "rust/op-reth/crates/trie/src/db/store.rs:733"
  - "rust/op-reth/crates/trie/src/db/store.rs:694"
  - "rust/op-reth/crates/trie/src/db/store.rs:525"
bug_class: missing-integrity-check
tags:
  - infrastructure
  - storage
  - state-integrity
  - proof-storage
  - append-ordering
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence shows one real runtime change in the MDBX-backed op-proofs trie store: a parent-hash continuity check was added before appending a new block state diff. That supports an integrity-hardening interpretation for append ordering, but the evidence does not establish an actual vulnerability, attacker reachability, or concrete security impact.

## Observed Patch Facts

1. In `rust/op-reth/crates/trie/src/db/store.rs`, the patch replaces `let entry =` with `let entry = match account_trie_cursor.seek_by_key_subkey(key.clone(), block_number)? {`.

2. In `rust/op-reth/crates/trie/src/db/store.rs`, the patch replaces `let entry =` with `let entry = match hashed_storage_cursor.seek_by_key_subkey(key.clone(), block_number)? {`.

3. In `rust/op-reth/crates/trie/src/db/store.rs`, the patch replaces `let entry =` with `let entry = match storage_trie_cursor.seek_by_key_subkey(key.clone(), block_number)? {`.

4. In `rust/op-reth/crates/trie/src/db/store.rs`, the patch changes a sensitive implementation path.

## Project Context

The changed code sits primarily in `rust/op-reth/crates/trie/src/db`, `rust/op-reth/crates/trie/src`, which anchors the finding in the `storage` area of the project. Historical context from `rust/op-reth/crates/trie/src/db/cursor.rs`, `rust/op-reth/crates/trie/src/initialize.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rust/op-reth/crates/trie/src/db/cursor.rs`, `rust/op-reth/crates/trie/src/initialize.rs`. The strongest project-level identifiers around this patch are `block_number`, `entry`, `match`, and `seek_by_key_subkey`.

## Before/After Behavior

Before the patch, the shown write path in `store_trie_updates_append_only_inner` derived `block_number` and, in the provided snippet, did not visibly reject an incoming `block_ref` whose parent hash differed from the latest stored tip. After the patch, it calls `get_latest_block_number_hash_inner()`, compares `latest_block_hash` to `block_ref.parent`, and returns `OpProofsStorageError::OutOfOrder` on mismatch before continuing. The other displayed hunks in `fetch_trie_updates` are formatting-only in the provided evidence and should not be treated as behavioral fixes.

# Root Cause

The append-only storage path lacked an explicit chain-continuity check at the write entry point, so out-of-order or mismatched block references were not visibly rejected there in the supplied pre-patch code.

## Walkthrough

1. `store_trie_updates_append_only_inner` is the only provided hunk showing a substantive behavioral change.

2. The new code loads the latest stored block number/hash via `get_latest_block_number_hash_inner()`.

3. It compares the stored tip hash with `block_ref.parent`.

4. If they differ, the function now returns `OpProofsStorageError::OutOfOrder` before performing the append-only write.

5. The `fetch_trie_updates` snippets still show exact block-number checks during reconstruction, but the provided before/after lines there are reformatting only.

6. Because the evidence shows a guard addition but not an exploit or externally reachable misuse path, the security thesis is not established.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rust/op-reth/crates/trie/src/db/store.rs | 525 | append-only trie update write path now enforces parent-hash continuity before accepting a new block state diff |
| rust/op-reth/crates/trie/src/db/store.rs | 665 | account trie history reconstruction path requires exact block-number match or errors |
| rust/op-reth/crates/trie/src/db/store.rs | 694 | storage trie history reconstruction path requires exact block-number match or errors |
| rust/op-reth/crates/trie/src/db/store.rs | 727 | hashed storage history reconstruction path requires exact block-number match or errors |

## Code Snippets

## Snippet 1

Context: `rust/op-reth/crates/trie/src/db/store.rs:676` (changes a sensitive control or state-update path)

Before
```rust
let mut trie_updates = TrieUpdates::default();
        for key in change_set.account_trie_keys {
            let entry =
                match account_trie_cursor.seek_by_key_subkey(key.clone(), block_number)? {
                    Some(v) if v.block_number == block_number => v.value.0,
                    _ => {
                        return Err(OpProofsStorageError::MissingAccountTrieHistory(
                            key.0,
```
After
```rust
let mut trie_updates = TrieUpdates::default();
        for key in change_set.account_trie_keys {
            let entry = match account_trie_cursor.seek_by_key_subkey(key.clone(), block_number)? {
                Some(v) if v.block_number == block_number => v.value.0,
                _ => {
                    return Err(OpProofsStorageError::MissingAccountTrieHistory(
                        key.0,
                        block_number,
```

## Snippet 2

Context: `rust/op-reth/crates/trie/src/db/store.rs:733` (changes a sensitive control or state-update path)

Before
```rust
for key in change_set.hashed_storage_keys {
            let entry =
                match hashed_storage_cursor.seek_by_key_subkey(key.clone(), block_number)? {
                    Some(v) if v.block_number == block_number => v.value.0,
                    _ => {
                        return Err(OpProofsStorageError::MissingHashedStorageHistory {
                            hashed_address: key.hashed_address,
```
After
```rust
for key in change_set.hashed_storage_keys {
            let entry = match hashed_storage_cursor.seek_by_key_subkey(key.clone(), block_number)? {
                Some(v) if v.block_number == block_number => v.value.0,
                _ => {
                    return Err(OpProofsStorageError::MissingHashedStorageHistory {
                        hashed_address: key.hashed_address,
                        hashed_storage_key: key.hashed_storage_key,
```

## Snippet 3

Context: `rust/op-reth/crates/trie/src/db/store.rs:694` (changes a sensitive control or state-update path)

Before
```rust
for key in change_set.storage_trie_keys {
            let entry =
                match storage_trie_cursor.seek_by_key_subkey(key.clone(), block_number)? {
                    Some(v) if v.block_number == block_number => v.value.0,
                    _ => {
                        return Err(OpProofsStorageError::MissingStorageTrieHistory(
                            key.hashed_address,
```
After
```rust
for key in change_set.storage_trie_keys {
            let entry = match storage_trie_cursor.seek_by_key_subkey(key.clone(), block_number)? {
                Some(v) if v.block_number == block_number => v.value.0,
                _ => {
                    return Err(OpProofsStorageError::MissingStorageTrieHistory(
                        key.hashed_address,
                        key.path.0,
```

## Snippet 4

Context: `rust/op-reth/crates/trie/src/db/store.rs:525` (changes signature or replay validation logic)

Before
```rust
fn store_trie_updates_append_only_inner(
         &self,
         block_ref: BlockWithParent,
         block_state_diff: BlockStateDiff,
     ) -> OpProofsStorageResult<WriteCounts> {
         let block_number = block_ref.block.number;
```
After
```rust
fn store_trie_updates_append_only_inner(
        &self,
        block_ref: BlockWithParent,
        block_state_diff: BlockStateDiff,
    ) -> OpProofsStorageResult<WriteCounts> {
        let block_number = block_ref.block.number;
```

# Fix Pattern

Add a pre-mutation invariant check to an append-only storage path so writes are rejected unless they extend the current tip.

## How It Was Fixed

The write path now verifies parent-hash continuity against the latest stored block before accepting a new `BlockStateDiff`, failing closed with `OutOfOrder` when the append would be out of sequence.

# Why It Matters

1. Prevents inconsistent append order from being accepted into proof/trie storage.

2. Strengthens internal state integrity for a replay-sensitive storage pipeline.

3. Does not, by itself, prove a security vulnerability or attacker-exploitable condition.

# Evidence Notes

Strongest evidence is `rust/op-reth/crates/trie/src/db/store.rs:525`, where a new parent-hash check rejects out-of-order appends. The `fetch_trie_updates` hunks at `:665`, `:694`, and `:727` remain useful subsystem context but are formatting-only in the provided diff. The commit subject, `fmt + clippy + doc fixes`, also weighs against making a strong vulnerability claim from this evidence alone. Protocol security invariant: Append-only proof/trie storage should only accept a new block state diff when it extends the current stored tip, and versioned history reconstruction should fail closed when an exact block version is unavailable. Verification notes: The patch does not prove a remotely reachable attacker can supply out-of-order block_ref inputs. The patch does not by itself prove that invalid proofs were emitted or accepted before the guard was added. The fetch_trie_updates hunks shown here are formatting-only and should not be treated as separate security fixes. The evidence does not establish consensus failure, fund loss, or cross-node compromise impact. Behavioral change is clearly shown only for the append-order guard. No supplied evidence shows attacker control over `block_ref` inputs. No supplied evidence shows prior proof corruption, consensus failure, or user-impacting exploit. No tests or regression case are included here to demonstrate a security bug scenario. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-integrity-check`
Final tags: `infrastructure, storage, state-integrity, proof-storage, append-ordering`

The supplied evidence shows one real behavioral change: the append-only op-proofs trie storage path now verifies that the incoming block extends the current stored tip by comparing the latest stored hash with `block_ref.parent`, and rejects mismatches with `OutOfOrder`. In a proof/trie storage path, that is a meaningful integrity hardening measure. However, the patch does not demonstrate attacker reachability, prior proof corruption, or a concrete exploit, so this is better retained as security hardening rather than a confirmed security fix.

## Security Evidence

1. Adds a parent-hash continuity check before append-only trie writes.
2. Fails closed with `OpProofsStorageError::OutOfOrder` when the new block does not extend the stored tip.
3. The changed code is in op-proofs trie storage, an integrity- and replay-sensitive subsystem.
4. The other cited `fetch_trie_updates` hunks are formatting-only and do not weaken the hardening interpretation of the continuity check.

## Missing Evidence

1. No supplied test or regression shows a real pre-patch exploit scenario.
2. No evidence shows untrusted or attacker-controlled input can reach this write path.
3. No evidence shows invalid proofs, consensus breakage, or user-visible compromise before the change.
4. The commit subject `fmt + clippy + doc fixes` does not independently support a strong vulnerability claim.

## Claim Boundaries

1. Supported: the patch hardens append-order/state-continuity validation in proof storage.
2. Not supported: a concrete exploitable security bug was definitively fixed.
3. Not supported: the formatting-only history-reconstruction hunks are separate security fixes.
4. Do not claim fund loss, remote compromise, or consensus failure from this patch alone.
