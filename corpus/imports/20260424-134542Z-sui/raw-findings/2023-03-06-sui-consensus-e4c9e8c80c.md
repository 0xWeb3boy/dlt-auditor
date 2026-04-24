---
case_id: case_20230306_e4c9e8c80c
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
source_quality: high
date: 2023-03-06
source_refs:
  - git:e4c9e8c80cfc426e3a0483e17d041864393087c1
  - "crates/sui-core/src/consensus_handler.rs:101"
  - "crates/sui-core/src/consensus_handler.rs:196"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:1742"
  - "narwhal/types/src/consensus.rs:61"
bug_class: unverified-consensus-timestamp-source
impact_type:
  - integrity-risk
  - consensus-timestamp-integrity
confidence: medium
tags:
  - blockchain-core
  - consensus
  - timestamp-validation
  - trust-boundary
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch likely fixes a security-relevant consensus timestamp-source bug. The consensus handler previously passed `consensus_output.sub_dag.leader.metadata.created_at` into the consensus commit prologue. The commit message states that certificate metadata timestamps are not verified and could lead to security issues. The patch instead selects `consensus_output.sub_dag.leader.header.created_at`, with an in-code comment that Narwhal enforces invariants on that header timestamp, and passes the selected timestamp into both commit prologue and commit boundary handling.

## Observed Patch Facts

1. In `crates/sui-core/src/consensus_handler.rs`, the patch replaces `let round = consensus_output.sub_dag.round();` with `let round = consensus_output.sub_dag.leader_round();`.

2. In `crates/sui-core/src/consensus_handler.rs`, the patch replaces `.handle_commit_boundary(&consensus_output.sub_dag, &self.checkpoint_service)` with `.handle_commit_boundary(round, timestamp, &self.checkpoint_service)`.

3. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch replaces `committed_dag: &Arc<CommittedSubDag>,` with `round: Round,`.

4. In `narwhal/types/src/consensus.rs`, the patch replaces `pub fn round(&self) -> Round {` with `pub fn leader_round(&self) -> Round {`.

## Project Context

The changed code sits primarily in `crates/sui-core/src`, `crates/sui-core`, `crates/sui-core/src/authority`, which anchors the finding in the `consensus` area of the project. Historical context from `narwhal/types/src/primary.rs`, `narwhal/types/src/error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `narwhal/types/src/primary.rs`, `narwhal/types/src/error.rs`. The strongest project-level identifiers around this patch are `round`, `consensus_output`, `sub_dag`, and `timestamp`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/narwhal_manager_tests.rs`, `crates/sui-core/src/unit_tests/authority_tests.rs`.

## Before/After Behavior

Before the patch, consensus commit processing used the leader certificate metadata `created_at` timestamp for the commit prologue, and commit boundary handling received the broader committed sub-DAG. After the patch, `handle_consensus_output` explicitly selects the leader round and `leader.header.created_at`, then passes those primitive values to `consensus_commit_prologue_transaction` and `handle_commit_boundary`. `AuthorityPerEpochStore::handle_commit_boundary` now accepts `round` and `timestamp_ms` directly. The `CommittedSubDag::round()` accessor was renamed to `leader_round()` while still returning `self.leader.round()`.

# Root Cause

The supported root cause is that consensus commit handling used `leader.metadata.created_at`, which the commit message describes as unverified, as a timestamp source. The evidence supports replacing that source with `leader.header.created_at`, which the patched code says has Narwhal-enforced invariants. The evidence does not establish a concrete exploit path or specific downstream failure mode.

## Walkthrough

1. `handle_consensus_output` processes a `ConsensusOutput` containing a committed sub-DAG and leader certificate.

2. Before the fix, the consensus commit prologue received `consensus_output.sub_dag.leader.metadata.created_at` as its timestamp.

3. The commit message identifies certificate metadata timestamps as unverified and security-relevant.

4. After the fix, the handler extracts `round` via `consensus_output.sub_dag.leader_round()`.

5. It extracts `timestamp` via `consensus_output.sub_dag.leader.header.created_at`.

6. The patched code comments that Narwhal enforces invariants on `header.created_at`.

7. The selected `round` and header timestamp are passed to `consensus_commit_prologue_transaction(round, timestamp)`.

8. The same selected values are passed to `handle_commit_boundary(round, timestamp, &self.checkpoint_service)`.

9. `AuthorityPerEpochStore::handle_commit_boundary` now receives `round` and `timestamp_ms` directly instead of receiving the full committed sub-DAG.

10. The `round()` to `leader_round()` rename is supporting clarity, not the root security fix.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/consensus_handler.rs | 101 | Selects consensus leader round and trusted header timestamp from ConsensusOutput before building transactions and the commit prologue. |
| crates/sui-core/src/consensus_handler.rs | 196 | Passes the selected round and header timestamp into commit boundary handling for checkpoint notification. |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 1742 | Handles commit boundary using caller-provided consensus round and checkpoint timestamp rather than deriving them from the committed sub-DAG. |
| narwhal/types/src/consensus.rs | 61 | Renames CommittedSubDag round accessor to leader_round, clarifying that the round used is the leader certificate round. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/consensus_handler.rs:101` (changes a consensus- or validator-sensitive branch)

Before
```rust
let mut bytes = 0usize;
        let round = consensus_output.sub_dag.round();

        /* (serialized, transaction, output_cert) */
        let mut transactions = vec![];

        let prologue_transaction = self.consensus_commit_prologue_transaction(
```
After
```rust
let mut bytes = 0usize;
        let round = consensus_output.sub_dag.leader_round();

        /* (serialized, transaction, output_cert) */
        let mut transactions = vec![];
        // Narwhal enforces some invariants on the header.created_at, so we can use it as a timestamp
        let timestamp = consensus_output.sub_dag.leader.header.created_at;
```

## Snippet 2

Context: `crates/sui-core/src/consensus_handler.rs:196` (changes a consensus- or validator-sensitive branch)

Before
```rust
self.epoch_store
            .handle_commit_boundary(&consensus_output.sub_dag, &self.checkpoint_service)
            .expect("Unrecoverable error in consensus handler when processing commit boundary")
    }
```
After
```rust
self.epoch_store
            .handle_commit_boundary(round, timestamp, &self.checkpoint_service)
            .expect("Unrecoverable error in consensus handler when processing commit boundary")
    }
```

## Snippet 3

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:1742` (changes a consensus- or validator-sensitive branch)

Before
```rust
pub fn handle_commit_boundary<C: CheckpointServiceNotify>(
        &self,
        committed_dag: &Arc<CommittedSubDag>,
        checkpoint_service: &Arc<C>,
    ) -> SuiResult {
        let round = committed_dag.round();
        debug!("Commit boundary at {}", round);
        // This exchange is restart safe because of following:
```
After
```rust
pub fn handle_commit_boundary<C: CheckpointServiceNotify>(
        &self,
        round: Round,
        timestamp_ms: CheckpointTimestamp,
        checkpoint_service: &Arc<C>,
    ) -> SuiResult {
        debug!("Commit boundary at {}", round);
        // This exchange is restart safe because of following:
```

## Snippet 4

Context: `narwhal/types/src/consensus.rs:61` (changes a sensitive control or state-update path)

Before
```rust
}

    pub fn round(&self) -> Round {
        self.leader.round()
    }
```
After
```rust
}

    pub fn leader_round(&self) -> Round {
        self.leader.round()
    }
```

# Fix Pattern

Replace use of an unverified metadata timestamp with a timestamp field documented as having consensus-enforced invariants, and pass the selected primitive value explicitly through downstream commit-boundary APIs.

## How It Was Fixed

The patch changed the timestamp source in `crates/sui-core/src/consensus_handler.rs` from `leader.metadata.created_at` to `leader.header.created_at`. It reused that selected timestamp for consensus commit prologue creation and commit boundary handling. It also changed `AuthorityPerEpochStore::handle_commit_boundary` to accept `round` and `timestamp_ms` directly, and renamed the committed sub-DAG round accessor to `leader_round()` for clarity.

# Why It Matters

1. The old timestamp source is described by the commit message as unverified.

2. Consensus commit prologue logic consumes the selected timestamp.

3. Checkpoint boundary handling also receives the selected timestamp after the patch.

4. Using a consensus-checked timestamp source reduces reliance on mixed-trust certificate metadata.

5. The evidence does not prove checkpoint forgery, signature bypass, transaction validity bypass, or consensus divergence.

# Evidence Notes

Primary evidence is commit `e4c9e8c80cfc426e3a0483e17d041864393087c1`, whose message says certificate metadata timestamps were used instead of header timestamps and that metadata timestamps do not have verification. Code evidence shows `consensus_handler.rs` now selecting `consensus_output.sub_dag.leader.header.created_at` and passing it to both `consensus_commit_prologue_transaction(round, timestamp)` and `handle_commit_boundary(round, timestamp, &self.checkpoint_service)`. Code evidence also shows `authority_per_epoch_store.rs` changing `handle_commit_boundary` to accept `round` and `timestamp_ms` directly. The exact Narwhal invariants on header timestamps are only referenced by an in-code comment and are not shown in the supplied excerpts. Protocol security invariant: Consensus commit processing should use a timestamp source whose relevant invariants are enforced by consensus data, rather than an unverified certificate metadata timestamp. Verification notes: The patch does not prove a concrete exploit path or attacker capability. The evidence does not show that forged metadata timestamps could independently cause consensus divergence. The evidence does not show checkpoint forgery, signature bypass, or transaction validity bypass. The exact Narwhal header timestamp invariants are referenced but not fully shown in the provided context. The round accessor rename is supporting clarity, not by itself a security fix. Supported: timestamp source changed from certificate metadata to leader header. Supported: commit message explicitly frames metadata timestamps as unverified and security-relevant. Supported: commit prologue and commit boundary paths now receive the selected header timestamp. Not supported: a concrete attacker model or exploit path. Not supported: claims of checkpoint forgery, signature bypass, transaction validity bypass, or proven consensus divergence. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `unverified-consensus-timestamp-source`
Final impact type: `integrity-risk, consensus-timestamp-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, timestamp-validation, trust-boundary, security-hardening`

The supplied evidence supports keeping this as security-relevant, but the safer corpus classification is security-hardening rather than a proven security-fix. The commit message explicitly says certificate metadata timestamps were unverified and could lead to security issues, and the patch replaces that source with a header timestamp described as having Narwhal-enforced invariants. However, the excerpts do not prove a concrete exploit path, attacker capability, consensus divergence, checkpoint forgery, or other specific impact.

## Security Evidence

1. Commit body explicitly identifies use of certificate metadata timestamps as a serious problem that could lead to security issues because metadata timestamps are not verified.
2. Consensus handling changed from using leader metadata created_at to leader.header.created_at.
3. Patched code comments that Narwhal enforces invariants on header.created_at.
4. The selected header timestamp is passed into consensus commit prologue and commit boundary handling.
5. The affected code is in consensus and checkpoint-boundary processing paths.

## Missing Evidence

1. No concrete attacker model is shown.
2. No exploit path from forged metadata timestamp to consensus failure or checkpoint corruption is demonstrated.
3. The actual Narwhal invariants on header.created_at are referenced but not included in the supplied evidence.
4. No tests or assertions demonstrate the rejected unsafe timestamp behavior.
5. No evidence proves signature bypass, transaction validity bypass, or consensus divergence.

## Claim Boundaries

1. Supported: the patch removes reliance on an unverified metadata timestamp in consensus commit processing.
2. Supported: the change tightens timestamp trust assumptions in a consensus-sensitive path.
3. Not supported: a confirmed exploitable vulnerability with a demonstrated impact.
4. Not supported: classifying the impact specifically as consensus failure from the supplied patch alone.
5. The round accessor rename is supporting cleanup and not independently security-relevant.
