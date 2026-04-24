---
case_id: case_20230109_4c780d87db
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2023-01-09
source_refs:
  - git:4c780d87db8a82eaf4af93f97ae4f293367f0503
  - "crates/sui-core/src/checkpoints/checkpoint_executor/mod.rs:626"
  - "crates/sui-core/src/checkpoints/mod.rs:528"
  - "crates/sui-core/src/authority.rs:2470"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:334"
bug_class: finality-rollback
impact_type:
  - finality-integrity
  - state-integrity
tags:
  - blockchain-core
  - consensus
  - checkpoint
  - state-sync
  - reconfiguration
  - finality
  - rollback
validation_status: completed
security_verdict: confirmed
validated_as: security-fix
keep_in_security_corpus: true
---


# Summary

The patch fixes an epoch-transition ordering bug where local rollback could revert a transaction that had already been executed through checkpoint processing. The evidence supports a consensus/finality integrity issue, but does not prove a remote exploit path, asset theft, signature bypass, or permanent chain-wide fork.

## Observed Patch Facts

1. In `crates/sui-core/src/checkpoints/checkpoint_executor/mod.rs`, the patch replaces `Ok(Ok(_)) => return Ok(()),` with `Ok(Ok(_)) => {`.

2. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `if self.epoch_store.tx_checkpointed_in_current_epoch(&digest)? {` with `if self`.

3. In `crates/sui-core/src/authority.rs`, the patch adds `if epoch_store.is_transaction_executed_in_checkpoint(&digest)? {`.

4. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch replaces `pub fn get_signed_transaction(` with `pub fn insert_executed_transactions(`.

## Project Context

The changed code sits primarily in `crates/sui-core/src/checkpoints/checkpoint_executor`, `crates/sui-core/src/checkpoints`, `crates/sui-core/src`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/sui-core/src/authority/authority_store.rs`, `crates/sui-core/src/transaction_orchestrator.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/authority/authority_store.rs`, `crates/sui-core/src/epoch/reconfiguration.rs`. The strongest project-level identifiers around this patch are `digest`, `epoch_store`, `batch`, and `insert_executed_transactions`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/batch_tests.rs`, `crates/sui-core/src/unit_tests/execution_driver_tests.rs`.

## Before/After Behavior

Before the patch, successful checkpoint execution returned without recording the executed transaction digests for rollback decisions, and `revert_uncommitted_epoch_transactions` reverted every pending consensus certificate. After the patch, checkpoint execution records executed digests in epoch storage, and the rollback path skips pending digests that are known to have been executed in a checkpoint.

# Root Cause

The rollback path treated membership in `pending_consensus_certificates` as sufficient evidence that a transaction was uncommitted. In the documented state-sync reconfiguration case, that local pending status could be stale because the transaction had already been executed through checkpoint processing.

## Walkthrough

1. A validator may have a transaction digest still present in its local pending consensus certificates.

2. The commit message describes an epoch ending via state sync before the validator reaches the end of the consensus stream.

3. In that ordering, the transaction may already have been executed as part of a checkpoint.

4. Before the fix, checkpoint execution did not persist the executed digests into epoch storage for rollback protection.

5. Before the fix, end-of-epoch cleanup reverted each pending certificate's state update unconditionally.

6. The patch adds epoch-store persistence mapping checkpoint-executed digests to checkpoint sequence numbers.

7. The checkpoint executor records `all_tx_digests` after successful checkpoint transaction execution.

8. The rollback path now checks whether a pending digest was executed in a checkpoint and skips reverting it when true.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/checkpoints/checkpoint_executor/mod.rs | 626 | records all transaction digests executed by checkpoint executor into epoch storage with checkpoint sequence |
| crates/sui-core/src/authority.rs | 2470 | guards end-of-epoch pending consensus transaction rollback by skipping checkpoint-executed digests |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 334 | adds epoch-store persistence for executed transaction digest to checkpoint mapping |
| crates/sui-core/src/checkpoints/mod.rs | 528 | updates checkpoint builder inclusion checks to use builder-specific checkpoint inclusion tracking |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/checkpoints/checkpoint_executor/mod.rs:626` (changes a consensus- or validator-sensitive branch)

Before
```rust
}
            Ok(Err(err)) => return Err(err),
            Ok(Ok(_)) => return Ok(()),
        }
    }
```
After
```rust
}
            Ok(Err(err)) => return Err(err),
            Ok(Ok(_)) => {
                epoch_store.insert_executed_transactions(&all_tx_digests, checkpoint_sequence)?;
                return Ok(());
            }
        }
    }
```

## Snippet 2

Context: `crates/sui-core/src/checkpoints/mod.rs:528` (changes a consensus- or validator-sensitive branch)

Before
```rust
for effect in roots {
                let digest = effect.transaction_digest;
                if self.epoch_store.tx_checkpointed_in_current_epoch(&digest)? {
                    continue;
                }
```
After
```rust
for effect in roots {
                let digest = effect.transaction_digest;
                if self
                    .epoch_store
                    .builder_included_transaction_in_checkpoint(&digest)?
                {
                    continue;
                }
```

## Snippet 3

Context: `crates/sui-core/src/authority.rs:2470` (changes a consensus- or validator-sensitive branch)

Before
```rust
);
        for digest in pending_certificates {
            debug!("Reverting {:?} at the end of epoch", digest);
            self.database.revert_state_update(&digest).await?;
```
After
```rust
);
        for digest in pending_certificates {
            if epoch_store.is_transaction_executed_in_checkpoint(&digest)? {
                debug!("Not reverting pending consensus transaction {:?} - it was included in checkpoint", digest);
                continue;
            }
            debug!("Reverting {:?} at the end of epoch", digest);
            self.database.revert_state_update(&digest).await?;
```

## Snippet 4

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:334` (changes a consensus- or validator-sensitive branch)

Before
```rust
}

    pub fn get_signed_transaction(
        &self,
```
After
```rust
}

    pub fn insert_executed_transactions(
        &self,
        digests: &[TransactionDigest],
        sequence: CheckpointSequenceNumber,
    ) -> SuiResult {
        let batch = self.tables.executed_transactions_to_checkpoint.batch();
```

# Fix Pattern

Persist finalization evidence at checkpoint execution time, then consult that evidence before performing end-of-epoch rollback.

## How It Was Fixed

`execute_transactions` now calls `epoch_store.insert_executed_transactions(&all_tx_digests, checkpoint_sequence)?` after successful checkpoint execution. `AuthorityPerEpochStore` gains persistence for executed transaction digests. `revert_uncommitted_epoch_transactions` now avoids `revert_state_update` for pending digests recorded as checkpoint-executed. The checkpoint builder change to `builder_included_transaction_in_checkpoint` is related bookkeeping, but the rollback guard is the core fix.

# Why It Matters

1. Preserves finality for checkpoint-executed transactions during reconfiguration.

2. Avoids local state rollback based on stale pending-consensus bookkeeping.

3. Protects a consensus-sensitive integrity invariant.

4. Evidence does not establish direct exploitability or concrete user asset loss.

# Evidence Notes

The strongest evidence is in `crates/sui-core/src/checkpoints/checkpoint_executor/mod.rs:626`, where executed checkpoint digests are now recorded; `crates/sui-core/src/authority/authority_per_epoch_store.rs:334`, where digest-to-checkpoint persistence is added; and `crates/sui-core/src/authority.rs:2470`, where rollback skips checkpoint-executed digests. The commit message explicitly states the problematic condition: a final transaction could be reverted when epoch end is learned through state sync before the local consensus stream catches up. Claims beyond local incorrect rollback and finality/integrity risk are not supported by the provided evidence. Protocol security invariant: A transaction executed as part of a checkpoint, including one learned through state sync during epoch transition, must not be reverted by end-of-epoch cleanup merely because it is still present in the local pending consensus set. Verification notes: No remote exploit path is shown by the patch evidence. No direct fund theft, unauthorized transaction execution, or signature bypass is proven. No chain-wide permanent fork is proven, only an incorrect local revert of a final/checkpointed transaction is supported. The fix relies on the stated assumption that local and state-synced checkpoints go through the checkpoint executor. The evidence supports a consensus/finality safety bug, not a confidentiality or access-control issue. Supported: incorrect rollback of checkpoint-executed transactions during epoch transition. Supported: fix records checkpoint-executed digests and checks them before rollback. Not supported: remote attacker trigger path. Not supported: direct theft, authorization bypass, or signature bypass. Not supported: permanent network-wide fork or guaranteed chain-wide consensus failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `confirmed`
Validated as: `security-fix`
Keep in security corpus: `true`
Final bug class: `finality-rollback`
Final impact type: `finality-integrity, state-integrity`
Final tags: `blockchain-core, consensus, checkpoint, state-sync, reconfiguration, finality, rollback`

The supplied evidence supports keeping this finding in a security-focused corpus. The commit and patch show a consensus/finality-sensitive bug where end-of-epoch cleanup could revert a transaction that had already been executed through checkpoint processing after state sync. The fix records checkpoint-executed transaction digests and consults that record before rollback. The original impact framing as generic consensus failure is slightly too broad, because the evidence supports local rollback of final/checkpointed state rather than a proven chain-wide fork or exploit path.

## Security Evidence

1. Commit message explicitly states a final transaction could be reverted during epoch transition after state sync.
2. Checkpoint execution now persists all executed transaction digests with checkpoint sequence information.
3. End-of-epoch rollback now skips pending consensus transactions already executed in a checkpoint.
4. The affected code is in validator authority, checkpoint executor, checkpoint builder, and epoch store paths.

## Missing Evidence

1. No attacker-controlled trigger path is shown.
2. No direct theft, authorization bypass, signature bypass, or confidentiality impact is shown.
3. No proof of permanent network-wide fork or chain-wide consensus halt is provided.

## Claim Boundaries

1. Supported claim: checkpoint-executed transactions could be incorrectly reverted during reconfiguration/state sync ordering.
2. Supported claim: the fix preserves finality/state integrity by recording and checking checkpoint execution status before rollback.
3. Unsupported claim: this proves direct remote exploitability or guaranteed chain-wide consensus failure.
