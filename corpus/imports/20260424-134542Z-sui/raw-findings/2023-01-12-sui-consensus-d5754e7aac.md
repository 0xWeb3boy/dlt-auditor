---
case_id: case_20230112_d5754e7aac
project: sui
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: consensus
confidence: medium
source_quality: high
date: 2023-01-12
source_refs:
  - git:d5754e7aac4a5d3d2e96e87a43a7379a219c3fda
  - "crates/sui-core/src/checkpoints/mod.rs:1174"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:941"
  - "crates/sui-core/src/authority/authority_per_epoch_store.rs:718"
  - "crates/sui-types/src/messages_checkpoint.rs:413"
bug_class: missing-signature-commitment
impact_type:
  - checkpoint-auditability
  - historical-integrity
tags:
  - checkpoint
  - signature
  - cryptographic-commitment
  - auditability
  - consensus
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch is best treated as checkpoint integrity hardening. It adds user signatures to checkpoint contents because the commit message states checkpoint history otherwise had no record of submitted user signatures after transaction signatures were removed from the TransactionDigest commitment. The evidence supports a missing historical commitment/auditability gap, but not claims of invalid signature acceptance, forgery, or broken consensus safety.

## Observed Patch Facts

1. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `let (output, mut result) = mpsc::channel::<(CheckpointContents, CheckpointSummary)>(10);` with `let all_digests: Vec<_> = store.iter().map(|(k, _v)| *k).collect();`.

2. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch replaces `fn finish_consensus_certificate_process_with_batch(` with `pub fn test_insert_user_signature(&self, digest: TransactionDigest, signature: &Signa...`.

3. In `crates/sui-core/src/authority/authority_per_epoch_store.rs`, the patch replaces `/// Returns Ok(true) if 2f+1 end of publish messages were recorded at this point` with `/// Note: this is async function as it waits for certificates to be processed by`.

4. In `crates/sui-types/src/messages_checkpoint.rs`, the patch adds `/// This field 'pins' user signatures for the checkpoint:`.

## Project Context

The changed code sits primarily in `crates/sui-core/src/checkpoints`, `crates/sui-core/src`, `crates/sui-core/src/authority`, which anchors the finding in the `consensus` area of the project. Historical context from `crates/sui-core/src/checkpoints/checkpoint_output.rs`, `crates/sui-types/src/messages.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-types/src/messages.rs`, `crates/sui-types/src/error.rs`. The strongest project-level identifiers around this patch are `digest`, `ConsensusTransactionKey::Certificate`, `signature`, and `transactions`. Nearby tests or test-like files include `crates/sui-core/src/unit_tests/authority_tests.rs`, `crates/sui-types/src/unit_tests/signature_seed_tests.rs`.

## Before/After Behavior

Before the change, CheckpointContents recorded transaction execution digests without user signatures. After the change, CheckpointContents includes an aligned user_signatures vector, with documented exceptions for genesis and final-epoch system transactions. AuthorityPerEpochStore gains a lookup that waits for certificate consensus processing before returning stored signatures for checkpoint construction, and tests seed signatures for checkpointed digests.

# Root Cause

Checkpoint contents did not include user signature material even though TransactionDigest no longer committed to transaction signatures, leaving checkpoint history without a durable record of the submitted authorization signatures.

## Walkthrough

1. CheckpointContents in crates/sui-types/src/messages_checkpoint.rs grows from only transactions to transactions plus user_signatures.

2. Inline documentation defines the expected alignment between transactions and signatures, with explicit exceptions for genesis and extra system transactions.

3. AuthorityPerEpochStore::user_signatures_for_checkpoint waits for each ConsensusTransactionKey::Certificate digest to be processed before retrieving signatures.

4. The commit message directly states the motivation: without this field, checkpoint history had no record of user signatures because TransactionDigest no longer committed to them.

5. The added test helper only supports tests by inserting signatures and marking the related consensus key processed; it is not itself the production root cause.

6. The checkpoint builder test now inserts default signatures for all test transaction digests so the new checkpoint contents path has signature data.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-types/src/messages_checkpoint.rs | 413 | Adds CheckpointContents.user_signatures to pin signatures alongside checkpointed transaction digests. |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 718 | Retrieves user signatures for checkpoint transaction digests after consensus certificate processing completes. |
| crates/sui-core/src/authority/authority_per_epoch_store.rs | 941 | Test helper inserts user signatures and marks the certificate consensus key processed. |
| crates/sui-core/src/checkpoints/mod.rs | 1174 | Checkpoint builder test setup now inserts user signatures for all test transaction digests. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/checkpoints/mod.rs:1174` (changes signature or replay validation logic)

Before
```rust
);
        }

        let (output, mut result) = mpsc::channel::<(CheckpointContents, CheckpointSummary)>(10);
```
After
```rust
);
        }
        let all_digests: Vec<_> = store.iter().map(|(k, _v)| *k).collect();
        for digest in all_digests {
            let signature = Signature::Ed25519SuiSignature(Default::default());
            state
                .epoch_store()
                .test_insert_user_signature(digest, &signature);
```

## Snippet 2

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:941` (changes signature or replay validation logic)

Before
```rust
}

    fn finish_consensus_certificate_process_with_batch(
        &self,
```
After
```rust
}

    pub fn test_insert_user_signature(&self, digest: TransactionDigest, signature: &Signature) {
        self.tables
            .user_signatures_for_checkpoints
            .insert(&digest, signature)
            .unwrap();
        let key = ConsensusTransactionKey::Certificate(digest);
```

## Snippet 3

Context: `crates/sui-core/src/authority/authority_per_epoch_store.rs:718` (changes signature or replay validation logic)

Before
```rust
}

    /// Returns Ok(true) if 2f+1 end of publish messages were recorded at this point
    pub fn record_end_of_publish(
```
After
```rust
}

    /// Note: this is async function as it waits for certificates to be processed by
    /// consensus before returning
    pub async fn user_signatures_for_checkpoint(
        &self,
        digests: &[TransactionDigest],
    ) -> SuiResult<Vec<Signature>> {
```

## Snippet 4

Context: `crates/sui-types/src/messages_checkpoint.rs:413` (changes signature or replay validation logic)

Before
```rust
pub struct CheckpointContents {
    transactions: Vec<ExecutionDigests>,
}
```
After
```rust
pub struct CheckpointContents {
    transactions: Vec<ExecutionDigests>,
    /// This field 'pins' user signatures for the checkpoint:
    ///
    /// * For normal checkpoint this field will contain same number of elements as transactions.
    /// * Genesis checkpoint has transactions but this field is empty.
    /// * Last checkpoint in the epoch will have (last)extra system transaction
    /// in the transactions list not covered in the signatures list
```

# Fix Pattern

Persist the missing cryptographic authorization material in the checkpoint data model and populate it from consensus-processed certificate state.

## How It Was Fixed

The change adds CheckpointContents.user_signatures, documents its relationship to checkpoint transactions, adds an epoch-store API to retrieve signatures after certificate processing, and updates checkpoint tests to seed signature data.

# Why It Matters

1. Preserves submitted user signature evidence in checkpoint history.

2. Addresses a commitment gap created when TransactionDigest stopped including transaction signatures.

3. Improves checkpoint auditability and historical integrity.

4. Does not establish that invalid signatures were previously accepted.

# Evidence Notes

Supported by the commit body and hunks adding CheckpointContents.user_signatures, AuthorityPerEpochStore::user_signatures_for_checkpoint, and related tests. Unsupported claims removed: consensus safety failure, runtime signature verification bypass, forged checkpoint contents, or demonstrated exploitability. Protocol security invariant: Checkpoint history should durably record the user signature material associated with checkpointed transactions when the transaction digest no longer commits to those signatures. Verification notes: The patch does not prove invalid transaction signatures could be accepted. The patch does not prove an attacker could forge checkpoint contents. The patch does not prove consensus safety or validator agreement was broken before the change. The provided evidence does not show runtime signature verification logic changing. The test helper changes are not themselves a production security fix. No evidence shows runtime signature verification logic changed. No evidence proves invalid transactions could be accepted before the patch. No evidence proves validator agreement or consensus safety was broken. Test helper changes should be treated as support code, not the root cause. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-signature-commitment`
Final impact type: `checkpoint-auditability, historical-integrity`
Final tags: `checkpoint, signature, cryptographic-commitment, auditability, consensus`

The supplied evidence supports retaining this as security hardening, not a concrete security fix. The commit explicitly says checkpoint history otherwise had no record of user signatures after TransactionDigest stopped committing to transaction signatures, and the patch adds a user_signatures field plus retrieval from consensus-processed certificate state. That is security-relevant integrity/auditability hardening around cryptographic authorization material, but the evidence does not prove invalid signature acceptance, forgery, state corruption, or consensus safety failure.

## Security Evidence

1. Commit body states checkpoint history lacked any record of submitted user signatures.
2. CheckpointContents gains a user_signatures field documented as pinning signatures to checkpoint contents.
3. AuthorityPerEpochStore adds user_signatures_for_checkpoint that waits for certificate consensus processing before returning signatures.
4. Tests are updated to seed signatures for checkpointed transaction digests.

## Missing Evidence

1. No evidence that invalid or forged transaction signatures were accepted before the patch.
2. No evidence that checkpoint contents could be forged or replayed in practice.
3. No evidence of broken validator agreement or consensus safety.
4. No evidence of runtime signature verification logic being fixed.

## Claim Boundaries

1. Classify as hardening of checkpoint signature retention, not state corruption.
2. Do not claim exploitability or signature bypass from the supplied patch alone.
3. Treat test helper changes as supporting coverage, not the production security fix.
4. Impact is historical integrity and auditability of checkpointed authorization material.
