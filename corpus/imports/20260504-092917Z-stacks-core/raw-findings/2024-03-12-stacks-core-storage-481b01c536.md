---
case_id: case_20240312_481b01c536
project: stacks-core
domain: validator-ops
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: storage
source_quality: high
date: 2024-03-12
source_refs:
  - git:481b01c5363ee7319a7f676c308a41d8ae34e3d1
  - "stacks-signer/src/signerdb.rs:208"
  - "stacks-signer/src/signerdb.rs:73"
  - "stacks-signer/src/signerdb.rs:129"
  - "stacks-signer/src/signerdb.rs:94"
bug_class: cross-cycle-stale-state
impact_type:
  - state-integrity
confidence: medium
tags:
  - validator-ops
  - storage
  - database
  - signer-state
  - stale-state
  - cycle-isolation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant stale-state issue in the signer database. It changes block storage, lookup, and removal from being keyed only by signer_signature_hash to being scoped by reward_cycle plus signer_signature_hash. The commit message explicitly says this prevents signers from acting on blocks from the previous cycle. The evidence supports a cross-cycle stale-state fix, but not a stronger claim about exploitability, fund loss, or consensus failure.

## Observed Patch Facts

1. In `stacks-signer/src/signerdb.rs`, the patch replaces `db.insert_block(&block_info)` with `let reward_cycle = 1;`.

2. In `stacks-signer/src/signerdb.rs`, the patch replaces `pub fn block_lookup(&self, hash: &Sha512Trunc256Sum) -> Result<Option<BlockInfo>, DBE...` with `pub fn block_lookup(`.

3. In `stacks-signer/src/signerdb.rs`, the patch replaces `pub fn remove_block(&mut self, hash: &Sha512Trunc256Sum) -> Result<(), DBError> {` with `pub fn remove_block(`.

4. In `stacks-signer/src/signerdb.rs`, the patch replaces `pub fn insert_block(&mut self, block_info: &BlockInfo) -> Result<(), DBError> {` with `pub fn insert_block(`.

## Project Context

The changed code sits primarily in `stacks-signer/src`, which anchors the finding in the `storage` area of the project. Historical context from `stacks-signer/src/signer.rs`, `stacks-signer/src/runloop.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `stacks-signer/src/signer.rs`, `stacks-signer/src/runloop.rs`. The strongest project-level identifiers around this patch are `block_info`, `block`, `hash`, and `reward_cycle`.

## Before/After Behavior

Before the patch, insert_block did not take a reward_cycle, block_lookup selected block_info using only signer_signature_hash, and remove_block deleted using only signer_signature_hash. After the patch, insert_block stores reward_cycle with the block record, block_lookup selects by reward_cycle and signer_signature_hash, and remove_block deletes by reward_cycle and signer_signature_hash. The updated test verifies that a block inserted for reward_cycle 1 is not returned when queried under reward_cycle 2.

# Root Cause

SignerDb treated signer_signature_hash as sufficient identity for persisted block_info, omitting reward_cycle from the database API and SQL predicates. That allowed records from different reward cycles to be conflated at lookup or removal boundaries.

## Walkthrough

1. SignerDb persisted serialized block_info records identified by signer_signature_hash.

2. Before the patch, block_lookup had no reward_cycle parameter and queried only by signer_signature_hash.

3. Before the patch, remove_block also targeted only signer_signature_hash.

4. The patch adds reward_cycle to insert_block, block_lookup, and remove_block.

5. insert_block now writes reward_cycle into the blocks table with signer_signature_hash and block_info.

6. block_lookup now requires both reward_cycle and signer_signature_hash to return block_info.

7. remove_block now requires both reward_cycle and signer_signature_hash to delete a record.

8. The regression test checks that a block stored under one reward cycle is not found under another reward cycle.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| stacks-signer/src/signerdb.rs | 75 | block_lookup now requires reward_cycle and selects block_info by reward_cycle plus signer_signature_hash |
| stacks-signer/src/signerdb.rs | 96 | insert_block now records block_info under an explicit reward_cycle |
| stacks-signer/src/signerdb.rs | 129 | remove_block now deletes only the block record matching both reward_cycle and signer_signature_hash |
| stacks-signer/src/signerdb.rs | 208 | test verifies a block stored for one reward_cycle is not returned for a different reward_cycle |

## Code Snippets

## Snippet 1

Context: `stacks-signer/src/signerdb.rs:208` (changes persisted or aggregate state handling)

Before
```rust
fn test_basic_signer_db_with_path(db_path: impl AsRef<Path>) {
        let mut db = SignerDb::new(db_path).expect("Failed to create signer db");
        let (block_info, block) = create_block();
        db.insert_block(&block_info)
            .expect("Unable to insert block into db");

        let block_info = db
            .block_lookup(&block.header.signer_signature_hash())
```
After
```rust
fn test_basic_signer_db_with_path(db_path: impl AsRef<Path>) {
        let mut db = SignerDb::new(db_path).expect("Failed to create signer db");
        let reward_cycle = 1;
        let (block_info, block) = create_block();
        db.insert_block(reward_cycle, &block_info)
            .expect("Unable to insert block into db");

        let block_info = db
```

## Snippet 2

Context: `stacks-signer/src/signerdb.rs:73` (changes signature or replay validation logic)

Before
```rust
/// Fetch a block from the database using the block's
    /// `signer_signature_hash`
    pub fn block_lookup(&self, hash: &Sha512Trunc256Sum) -> Result<Option<BlockInfo>, DBError> {
        let result: Option<String> = query_row(
            &self.db,
            "SELECT block_info FROM blocks WHERE signer_signature_hash = ?",
            &[format!("{}", hash)],
        )?;
```
After
```rust
/// Fetch a block from the database using the block's
    /// `signer_signature_hash`
    pub fn block_lookup(
        &self,
        reward_cycle: u64,
        hash: &Sha512Trunc256Sum,
    ) -> Result<Option<BlockInfo>, DBError> {
        let result: Option<String> = query_row(
```

## Snippet 3

Context: `stacks-signer/src/signerdb.rs:129` (changes signature or replay validation logic)

Before
```rust
/// Remove a block
    pub fn remove_block(&mut self, hash: &Sha512Trunc256Sum) -> Result<(), DBError> {
        debug!("Deleting block_info: sighash = {hash}");
        self.db.execute(
            "DELETE FROM blocks WHERE signer_signature_hash = ?",
            &[format!("{}", hash)],
        )?;
```
After
```rust
/// Remove a block
    pub fn remove_block(
        &mut self,
        reward_cycle: u64,
        hash: &Sha512Trunc256Sum,
    ) -> Result<(), DBError> {
        debug!("Deleting block_info: sighash = {hash}");
```

## Snippet 4

Context: `stacks-signer/src/signerdb.rs:94` (changes a sensitive control or state-update path)

Before
```rust
/// Insert a block into the database.
    /// `hash` is the `signer_signature_hash` of the block.
    pub fn insert_block(&mut self, block_info: &BlockInfo) -> Result<(), DBError> {
        let block_json =
            serde_json::to_string(&block_info).expect("Unable to serialize block info");
```
After
```rust
/// Insert a block into the database.
    /// `hash` is the `signer_signature_hash` of the block.
    pub fn insert_block(
        &mut self,
        reward_cycle: u64,
        block_info: &BlockInfo,
    ) -> Result<(), DBError> {
        let block_json =
```

# Fix Pattern

Bind persisted signer block state to its protocol cycle at every database boundary by including reward_cycle in insert, lookup, and delete operations.

## How It Was Fixed

The SignerDb API was updated to require reward_cycle for block insertion, lookup, and removal. SQL statements were changed to store reward_cycle and to filter SELECT and DELETE operations on both reward_cycle and signer_signature_hash. A test was added for negative lookup across reward cycles.

# Why It Matters

1. Prevents signerdb from returning block_info from a previous reward cycle for a current-cycle operation.

2. Keeps signer block state scoped to the protocol cycle where it is valid.

3. Reduces stale-state risk in signer decision storage.

4. Evidence does not establish attacker control, remote exploitability, or a concrete downstream consensus failure.

# Evidence Notes

Grounded evidence is limited to stacks-signer/src/signerdb.rs and the commit message. The changed code shows reward_cycle added to insert_block, block_lookup, and remove_block, with SQL predicates updated accordingly. The test verifies cross-cycle lookup isolation. The commit message states the intended prevention: signers should not take actions on blocks from the previous cycle. Claims about exploitability, consensus divergence, or financial impact are unsupported by the provided evidence. Protocol security invariant: Signer database block records should be scoped to the reward cycle in which they are valid, so a lookup or deletion for the active cycle cannot accidentally match block_info from a previous cycle. Verification notes: The patch does not prove that signer_signature_hash collisions or reuse across reward cycles are attacker-controllable. The patch does not show the exact downstream signer action that would be incorrectly taken on a stale block. The patch does not prove remote exploitability, fund loss, or consensus divergence by itself. The evidence supports a stale cross-cycle state fix, not a cryptographic primitive failure. Reviewed only the provided mapper, draft, commit metadata, and code excerpts. Downgraded confidence from high to medium because the exact downstream signer action and exploit path are not shown. Kept security_verdict as likely because the patch enforces a protocol-scoped signer-state invariant and the commit message ties it to preventing stale-cycle signer actions. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `cross-cycle-stale-state`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `validator-ops, storage, database, signer-state, stale-state, cycle-isolation`

The supplied evidence supports a security-hardening classification rather than a proven security-fix. The patch scopes signer database block insert, lookup, and removal by reward_cycle in addition to signer_signature_hash, and the commit message explicitly ties this to preventing signers from acting on blocks from a previous reward cycle. That is security-relevant in a validator/signer context, but the excerpts do not prove attacker control, exploitability, consensus failure, or concrete state corruption.

## Security Evidence

1. Commit body says blocks should be associated with a specific reward cycle so signers do not act on blocks from the previous cycle.
2. block_lookup changed from querying only signer_signature_hash to querying reward_cycle plus signer_signature_hash.
3. remove_block changed from deleting only by signer_signature_hash to deleting by reward_cycle plus signer_signature_hash.
4. insert_block now records reward_cycle alongside signer_signature_hash and block_info.
5. Regression test verifies a block stored under one reward cycle is not returned for a different reward cycle.

## Missing Evidence

1. No shown downstream signer action that would be incorrectly taken on stale block_info.
2. No proof that an attacker can cause or exploit cross-cycle signer_signature_hash reuse or stale database state.
3. No demonstrated consensus divergence, fund loss, slashing, or remote exploit path.
4. No broader code evidence showing this was reachable through an adversarial input path.

## Claim Boundaries

1. Retain as protocol signer-state hardening, not as a fully proven exploitable vulnerability.
2. Do not claim cryptographic signature verification failure; signer_signature_hash is used as a database key in the evidence.
3. Do not claim concrete state corruption beyond cross-cycle stale-state confusion risk.
4. Do not claim financial impact or consensus failure from the supplied patch alone.
