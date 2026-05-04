---
case_id: case_20230124_17ae4d1671
project: stacks-core
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2023-01-24
source_refs:
  - git:17ae4d1671106ac4581214be053ec6004c9c3b84
  - "src/burnchains/db.rs:1297"
  - "src/burnchains/db.rs:1523"
  - "src/burnchains/db.rs:1673"
  - "src/burnchains/db.rs:1142"
bug_class: fork-unaware-consensus-lookup
impact_type:
  - consensus-integrity
  - node-state-divergence
confidence: medium
tags:
  - consensus
  - burnchain
  - fork-awareness
  - database-lookup
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch appears to fix a consensus-relevant fork-awareness bug in burnchain database lookups. Before the change, some paths selected burnchain operations or anchor block commit metadata using identifiers that did not include burnchain fork context. The patch adds burn block hash/header context to operation lookup and changes anchor metadata selection so canonical fork context can be considered before choosing the commit used in affirmation-map construction.

## Observed Patch Facts

1. In `src/burnchains/db.rs`, the patch replaces `pub fn get_anchor_block_commit(` with `pub fn get_anchor_block_commit_metadatas(`.

2. In `src/burnchains/db.rs`, the patch replaces `pub fn get_heaviest_anchor_block(` with `pub fn get_heaviest_anchor_block<B: BurnchainHeaderReader>(`.

3. In `src/burnchains/db.rs`, the patch replaces `if let Some((commit, metadata)) = BurnchainDB::get_anchor_block_commit(conn, rc)? {` with `if let Some(metadata) =`.

4. In `src/burnchains/db.rs`, the patch replaces `fn inner_get_burnchain_op(conn: &DBConn, txid: &Txid) -> Option<BlockstackOperationTy...` with `fn inner_get_burnchain_op(`.

## Project Context

The changed code sits primarily in `src/burnchains`, which anchors the finding in the `consensus` area of the project. Historical context from `src/burnchains/burnchain.rs`, `src/burnchains/affirmation.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `src/burnchains/burnchain.rs`, `src/burnchains/affirmation.rs`. The strongest project-level identifiers around this patch are `conn`, `txid`, `block_commit_metadata`, and `metadata`. Nearby tests or test-like files include `src/burnchains/tests/affirmation.rs`, `src/burnchains/tests/mod.rs`.

## Before/After Behavior

Before the patch, `inner_get_burnchain_op()` queried `burnchain_db_block_ops` by `txid` alone. After the patch, it also takes `burn_header_hash` and constrains the query by `block_hash`. Before the patch, anchor block commit lookup returned at most one commit/metadata pair for an `anchor_block` reward cycle. After the patch, the accessor returns all matching metadata rows so later logic can select the canonical one. Before the patch, canonical affirmation-map construction used `get_anchor_block_commit(conn, rc)` directly. After the patch, it calls `get_canonical_anchor_block_commit_metadata(conn, indexer, rc)` and then loads the block commit using `metadata.burn_block_hash` plus `metadata.txid`.

# Root Cause

The supported root cause is fork-unaware database identity for burnchain consensus data. Some lookups used only `txid` or reward-cycle anchor fields, which could select data without proving it belonged to the burnchain fork being evaluated.

## Walkthrough

1. A burnchain operation lookup previously accepted only `conn` and `txid` and selected from `burnchain_db_block_ops` where `txid = ?`.

2. The fix changes the helper to accept `burn_header_hash` and query with both `txid = ?1` and `block_hash = ?2`.

3. Anchor block commit loading previously selected a single row for `anchor_block = ?1`.

4. The replacement accessor returns all `BlockCommitMetadata` rows for that reward cycle instead of collapsing the choice before fork-canonical selection.

5. The heaviest-anchor and canonical affirmation-map paths now receive/use `BurnchainHeaderReader` context, supporting fork-aware selection.

6. Canonical affirmation-map construction now selects canonical anchor metadata first, then loads the corresponding block commit by burn block hash and txid.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| src/burnchains/db.rs | 1142 | resolves burnchain operations by txid and burn block hash instead of txid alone |
| src/burnchains/db.rs | 1297 | returns all anchor block commit metadata for a reward cycle so later logic can select the fork-canonical one |
| src/burnchains/db.rs | 1523 | selects heaviest anchor block with burnchain header/indexer context for fork-aware validation |
| src/burnchains/db.rs | 1673 | builds canonical affirmation map using canonical anchor commit metadata and then loads the matching block commit by burn block hash and txid |

## Code Snippets

## Snippet 1

Context: `src/burnchains/db.rs:1297` (changes the branch that decides whether execution stops or continues)

Before
```rust
}

    pub fn get_anchor_block_commit(
        conn: &DBConn,
        reward_cycle: u64,
    ) -> Result<Option<(LeaderBlockCommitOp, BlockCommitMetadata)>, DBError> {
        let sql = "SELECT * FROM block_commit_metadata WHERE anchor_block = ?1";
        let args: &[&dyn ToSql] = &[&u64_to_sql(reward_cycle)?];
```
After
```rust
}

    pub fn get_anchor_block_commit_metadatas(
        conn: &DBConn,
        reward_cycle: u64,
    ) -> Result<Vec<BlockCommitMetadata>, DBError> {
        let sql = "SELECT * FROM block_commit_metadata WHERE anchor_block = ?1";
        let args: &[&dyn ToSql] = &[&u64_to_sql(reward_cycle)?];
```

## Snippet 2

Context: `src/burnchains/db.rs:1523` (changes bounds, limits, or capacity handling)

Before
```rust
/// Get the block-commit and block metadata for the anchor block with the heaviest affirmation
    /// weight.
    pub fn get_heaviest_anchor_block(
        conn: &DBConn,
    ) -> Result<Option<(LeaderBlockCommitOp, BlockCommitMetadata)>, DBError> {
        match query_row::<BlockCommitMetadata, _>(
                        conn, "SELECT block_commit_metadata.* \
                               FROM affirmation_maps JOIN block_commit_metadata ON affirmation_maps.affirmation_id = block_commit_metadata.affirmation_id \
```
After
```rust
/// Get the block-commit and block metadata for the anchor block with the heaviest affirmation
    /// weight.
    pub fn get_heaviest_anchor_block<B: BurnchainHeaderReader>(
        conn: &DBConn,
        indexer: &B,
    ) -> Result<Option<(LeaderBlockCommitOp, BlockCommitMetadata)>, DBError> {
        let sql = "SELECT block_commit_metadata.* \
                   FROM affirmation_maps JOIN block_commit_metadata ON affirmation_maps.affirmation_id = block_commit_metadata.affirmation_id \
```

## Snippet 3

Context: `src/burnchains/db.rs:1673` (changes the branch that decides whether execution stops or continues)

Before
```rust
);
        for rc in start_rc..last_reward_cycle {
            if let Some((commit, metadata)) = BurnchainDB::get_anchor_block_commit(conn, rc)? {
                let bhh = commit.block_header_hash.clone();
                let txid = metadata.txid.clone();
                let present = unconfirmed_oracle(commit, metadata);
                if present {
```
After
```rust
);
        for rc in start_rc..last_reward_cycle {
            if let Some(metadata) =
                BurnchainDB::get_canonical_anchor_block_commit_metadata(conn, indexer, rc)?
            {
                let bhh = metadata.burn_block_hash.clone();
                let txid = metadata.txid.clone();
                let commit = BurnchainDB::get_block_commit(conn, &bhh, &txid)?
```

## Snippet 4

Context: `src/burnchains/db.rs:1142` (changes persisted or aggregate state handling)

Before
```rust
}

    fn inner_get_burnchain_op(conn: &DBConn, txid: &Txid) -> Option<BlockstackOperationType> {
        let qry = "SELECT op FROM burnchain_db_block_ops WHERE txid = ?";

        match query_row(conn, qry, &[txid]) {
            Ok(res) => res,
            Err(e) => {
```
After
```rust
}

    fn inner_get_burnchain_op(
        conn: &DBConn,
        burn_header_hash: &BurnchainHeaderHash,
        txid: &Txid,
    ) -> Option<BlockstackOperationType> {
        let qry = "SELECT op FROM burnchain_db_block_ops WHERE txid = ?1 AND block_hash = ?2";
```

# Fix Pattern

Make consensus database lookups fork-aware by including burn block hash/header context and delaying single-row anchor selection until canonical fork context is available.

## How It Was Fixed

The patch updated operation lookup to include `block_hash`, replaced a single anchor commit accessor with one returning all matching metadata, threaded indexer/header-reader context into anchor selection paths, and loaded the final block commit by the selected metadata's burn block hash and txid.

# Why It Matters

1. Prevents consensus code from mixing burnchain operation data across competing forks.

2. Preserves fork consistency for anchor-block and affirmation-map construction.

3. Reduces risk of node state divergence from ambiguous txid-only or reward-cycle-only lookups.

4. Evidence supports consensus correctness impact, but not theft, privilege escalation, or proven remote exploitability.

# Evidence Notes

Grounded evidence is limited to `src/burnchains/db.rs` changes around operation lookup, anchor metadata retrieval, heaviest-anchor selection, and canonical affirmation-map construction. The malformed transaction decoding, panic-prone conversion, and denial-of-service claims from the heuristic baseline are unsupported and excluded. The security assessment rests on consensus/fork correctness, not on demonstrated exploitability. Protocol security invariant: Consensus-facing burnchain operations and anchor block metadata must be resolved in the burnchain fork where they were observed; txid-only or reward-cycle-only identifiers are insufficient when competing burnchain forks may contain distinct rows for the same logical operation or anchor cycle. Verification notes: The patch does not prove remote exploitability. The patch does not show malformed transaction decoding or panic-prone integer conversion despite the heuristic baseline suggesting that shape. The patch does not prove funds theft or direct privilege escalation. The patch does not show whether txid collisions across forks are attacker-forced or only naturally possible through burnchain reorgs. The patch does not establish impact beyond consensus/fork correctness and node state consistency. Confirmed by diff evidence: `inner_get_burnchain_op` changed from txid-only lookup to txid plus burn block hash lookup. Confirmed by diff evidence: anchor commit retrieval changed from one optional pair to a vector of metadata rows. Confirmed by diff evidence: canonical affirmation-map construction now uses canonical metadata and reloads the commit by burn block hash and txid. Not established: attacker control, remote exploit path, funds loss, or direct crash condition. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `fork-unaware-consensus-lookup`
Final impact type: `consensus-integrity, node-state-divergence`
Final confidence: `medium`
Final tags: `consensus, burnchain, fork-awareness, database-lookup, security-hardening`

The supplied patch evidence supports a consensus-sensitive hardening case: burnchain operation and anchor metadata lookups are changed to include burnchain fork context instead of selecting by txid or reward-cycle fields alone. That is security-relevant in a blockchain consensus subsystem because fork-unaware selection can affect canonical state construction, but the evidence does not prove an attacker-controlled exploit, concrete chain split, crash, or liveness failure. The original security-fix classification is too strong; security-hardening is the conservative validated classification.

## Security Evidence

1. Commit subject explicitly says burnchain operations should always consider the burnchain fork in which they live.
2. inner_get_burnchain_op changes from txid-only lookup to txid plus block_hash lookup.
3. Anchor block commit lookup changes from returning a single row to returning all matching metadata so canonical selection can occur later.
4. Canonical affirmation-map construction now selects canonical anchor metadata using indexer/header-reader context and reloads the commit by burn block hash plus txid.
5. Changed code is in burnchain database and affirmation-map paths, which are consensus-sensitive.

## Missing Evidence

1. No demonstrated attacker-controlled path or exploit scenario is shown.
2. No proof of funds loss, privilege escalation, or direct denial of service is provided.
3. No concrete evidence that the old behavior caused an actual consensus split or liveness failure.
4. No tests or assertions in the supplied evidence show the failure mode being triggered.

## Claim Boundaries

1. Validate as consensus security hardening, not a proven security fix.
2. Impact should be limited to fork-aware consensus data selection and node state consistency.
3. Do not claim malformed transaction handling, panic-prone decoding, theft, or privilege escalation.
4. Do not claim exploitability beyond the risk implied by fork-unaware consensus lookups.
