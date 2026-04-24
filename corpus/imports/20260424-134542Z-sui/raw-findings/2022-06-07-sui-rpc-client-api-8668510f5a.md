---
case_id: case_20220607_8668510f5a
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: rpc-client-api
source_quality: high
date: 2022-06-07
source_refs:
  - git:8668510f5a5b335c3c2a6219736d42693372d929
  - "crates/sui-core/src/checkpoints/mod.rs:139"
  - "crates/sui-core/src/checkpoints/mod.rs:913"
  - "crates/sui-core/src/authority_active/checkpoint_driver/mod.rs:554"
  - "crates/sui-core/src/checkpoints/mod.rs:666"
bug_class: checkpoint-integrity-hardening
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - checkpoints
  - consensus
  - state-integrity
  - hash-chaining
  - content-digest-validation
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch changes Sui checkpoint handling by adding a previous checkpoint digest to checkpoint summary/proposal construction paths and by comparing fetched checkpoint contents against content_digest instead of the whole checkpoint digest. These are consensus/checkpoint integrity-related changes, but the supplied evidence does not prove a concrete security vulnerability or attack path, so this should not be kept as a confirmed vulnerability fix.

## Observed Patch Facts

1. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `// Manage persistent local variables` with `fn get_prev_checkpoint_digest(`.

2. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `let sequence_number = self.next_checkpoint();` with `let checkpoint_sequence = self.next_checkpoint();`.

3. In `crates/sui-core/src/authority_active/checkpoint_driver/mod.rs`, the patch replaces `// TODO: check here that the digest of contents matches` with `// Check here that the digest of contents matches`.

4. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `let summary = CheckpointSummary::new(next_sequence_number, &contents);` with `let previous_digest = self`.

## Project Context

The changed code sits primarily in `crates/sui-core/src/checkpoints`, `crates/sui-core/src`, `crates/sui-core/src/authority_active/checkpoint_driver`, which anchors the finding in the `rpc-client-api` area of the project. Historical context from `crates/sui-core/src/checkpoints/proposal.rs`, `crates/sui-core/src/checkpoints/reconstruction.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/checkpoints/proposal.rs`, `crates/sui-core/src/safe_client.rs`. The strongest project-level identifiers around this patch are `checkpoint`, `digest`, `contents`, and `CheckpointSummary::new`. Nearby tests or test-like files include `crates/sui-core/src/checkpoints/tests/checkpoint_tests.rs`, `crates/sui-core/src/unit_tests/batch_tests.rs`.

## Before/After Behavior

Before the patch, the shown checkpoint construction and proposal paths created checkpoint summaries/proposals without passing a previous checkpoint digest, and the checkpoint driver compared downloaded contents.digest() to checkpoint.checkpoint.digest. After the patch, those construction paths retrieve the prior checkpoint digest when available and pass it into CheckpointSummary/SignedCheckpoint creation, while downloaded contents are checked against checkpoint.checkpoint.content_digest.

# Root Cause

The changed code lacked an explicit previous-checkpoint digest in the shown checkpoint creation/proposal paths, and one synchronization check used the whole checkpoint digest where the content digest was the relevant commitment. The evidence does not establish that these issues allowed checkpoint forgery, history rewriting, asset impact, or authorization bypass.

## Walkthrough

1. CheckpointStore gains get_prev_checkpoint_digest, returning None for sequence 0 and otherwise loading the previous authenticated checkpoint digest from local storage.

2. Checkpoint reconstruction now retrieves the previous checkpoint digest before creating a CheckpointSummary.

3. Signed checkpoint proposal creation now retrieves and passes the previous checkpoint digest along the creation path.

4. The checkpoint driver now validates fetched checkpoint contents against checkpoint.checkpoint.content_digest.

5. No supplied evidence shows how an attacker could exploit the prior behavior or bypass other consensus checks.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/checkpoints/mod.rs | 139 | adds retrieval of the previous authenticated checkpoint digest for chain-linking new summaries/proposals |
| crates/sui-core/src/checkpoints/mod.rs | 666 | uses previous checkpoint digest when constructing a reconstructed checkpoint summary |
| crates/sui-core/src/checkpoints/mod.rs | 913 | includes previous checkpoint digest when creating a signed checkpoint proposal |
| crates/sui-core/src/authority_active/checkpoint_driver/mod.rs | 554 | validates downloaded checkpoint contents against the checkpoint content digest |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/checkpoints/mod.rs:139` (changes a consensus- or validator-sensitive branch)

Before
```rust
impl CheckpointStore {
    // Manage persistent local variables
```
After
```rust
impl CheckpointStore {
    fn get_prev_checkpoint_digest(
        &mut self,
        checkpoint_sequence: CheckpointSequenceNumber,
    ) -> Result<Option<CheckpointDigest>, SuiError> {
        // Extract the previous checkpoint digest if there is one.
        Ok(if checkpoint_sequence > 0 {
```

## Snippet 2

Context: `crates/sui-core/src/checkpoints/mod.rs:913` (changes a consensus- or validator-sensitive branch)

Before
```rust
// Include the sequence number of all extra transactions not already in a
        // checkpoint. And make a list of the transactions.
        let sequence_number = self.next_checkpoint();
        let next_local_tx_sequence = self.extra_transactions.values().max().unwrap() + 1;

        let transactions = CheckpointContents::new(self.extra_transactions.keys());
        let proposal = SignedCheckpointProposal(SignedCheckpoint::new(
            sequence_number,
```
After
```rust
// Include the sequence number of all extra transactions not already in a
        // checkpoint. And make a list of the transactions.
        let checkpoint_sequence = self.next_checkpoint();
        let next_local_tx_sequence = self.extra_transactions.values().max().unwrap() + 1;

        // Extract the previous checkpoint digest if there is one.
        let previous_digest = self.get_prev_checkpoint_digest(checkpoint_sequence)?;
```

## Snippet 3

Context: `crates/sui-core/src/authority_active/checkpoint_driver/mod.rs:554` (changes a consensus- or validator-sensitive branch)

Before
```rust
detail: Some(contents),
            }) => {
                // TODO: check here that the digest of contents matches
                if contents.digest() != checkpoint.checkpoint.digest {
                    // A byzantine authority!
                    // TODO: Report Byzantine authority
```
After
```rust
detail: Some(contents),
            }) => {
                // Check here that the digest of contents matches
                if contents.digest() != checkpoint.checkpoint.content_digest {
                    // A byzantine authority!
                    // TODO: Report Byzantine authority
```

## Snippet 4

Context: `crates/sui-core/src/checkpoints/mod.rs:666` (changes a consensus- or validator-sensitive branch)

Before
```rust
// Now create the new checkpoint and move all locals forward.
                    let summary = CheckpointSummary::new(next_sequence_number, &contents);
                    self.handle_internal_set_checkpoint(summary, &contents)
                        .map_err(FragmentInternalError::Error)?;
```
After
```rust
// Now create the new checkpoint and move all locals forward.
                    let previous_digest = self
                        .get_prev_checkpoint_digest(next_sequence_number)
                        .map_err(FragmentInternalError::Error)?;
                    let summary =
                        CheckpointSummary::new(next_sequence_number, &contents, previous_digest);
                    self.handle_internal_set_checkpoint(summary, &contents)
```

# Fix Pattern

Carry the previous checkpoint digest through checkpoint creation/proposal paths and validate fetched detail data against the digest field that commits to that detail data.

## How It Was Fixed

The patch added a helper to read the previous checkpoint digest, threaded that value into checkpoint summary and proposal creation, and corrected the checkpoint content validation comparison to use content_digest.

# Why It Matters

1. Touches consensus/checkpoint integrity code.

2. Improves explicit hash-linking between checkpoints in the shown paths.

3. Corrects validation of fetched checkpoint contents against the appropriate digest field.

4. Exploitability and concrete security impact are not demonstrated by the provided evidence.

# Evidence Notes

Grounded evidence comes from crates/sui-core/src/checkpoints/mod.rs and crates/sui-core/src/authority_active/checkpoint_driver/mod.rs. The claims that this prevents forged funds, arbitrary checkpoint rewriting, signature forgery, or a concrete consensus attack are unsupported. The evidence supports an integrity-related protocol change or hardening, not a confirmed vulnerability fix. Protocol security invariant: Checkpoint summaries and proposals should commit to the intended checkpoint contents and, after this change, to the previous checkpoint digest. Fetched checkpoint contents should be compared against the checkpoint content_digest field. The evidence supports this invariant change, but does not establish that the prior behavior was exploitable as a vulnerability. Verification notes: No exploit path is demonstrated by the patch evidence. No evidence shows funds, signatures, or transaction authorization could be directly forged. The previous behavior may also have caused sync/liveness failures; confidentiality or access-control impact is not shown. The patch does not prove accepted certified checkpoints could be arbitrarily rewritten without other consensus checks. No exploit path is shown. No direct asset, authorization, confidentiality, or signature impact is shown. Tests were mentioned in the commit file list, but their assertions are not provided in the input. Classified as unclear rather than likely because security relevance is plausible but not established. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `checkpoint-integrity-hardening`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, checkpoints, consensus, state-integrity, hash-chaining, content-digest-validation`

The evidence does not prove a concrete exploitable vulnerability, but it does show security-relevant hardening in a consensus/checkpoint subsystem: checkpoints are newly linked to the previous checkpoint digest, and fetched checkpoint contents are validated against the specific content digest commitment. That is enough to retain as security-hardening, not as a confirmed security fix.

## Security Evidence

1. CheckpointSummary and SignedCheckpointProposal construction now include the previous checkpoint digest.
2. A helper retrieves the digest of the previous authenticated checkpoint, creating explicit checkpoint hash-linking after genesis.
3. Remote checkpoint contents returned by another authority are now compared to checkpoint.checkpoint.content_digest instead of the whole checkpoint digest.
4. The affected code is in checkpoint reconstruction, proposal creation, and authority checkpoint synchronization paths.

## Missing Evidence

1. No demonstrated exploit path or attacker capability is provided.
2. No evidence shows prior checkpoints could be forged, rewritten, or accepted despite consensus signatures.
3. No test assertions are supplied showing a security regression case.
4. No direct asset loss, authorization bypass, confidentiality impact, or signature bypass is shown.

## Claim Boundaries

1. Classify as security-hardening, not security-fix.
2. Do not claim proven checkpoint forgery or history rewrite vulnerability.
3. Do not claim RPC-client API impact; the evidence is checkpoint/consensus focused.
4. Impact should be limited to state/checkpoint integrity hardening.
