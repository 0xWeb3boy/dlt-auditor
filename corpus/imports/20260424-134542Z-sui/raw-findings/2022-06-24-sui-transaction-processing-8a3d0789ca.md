---
case_id: case_20220624_8a3d0789ca
project: sui
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2022-06-24
source_refs:
  - git:8a3d0789caecb5751036a2b308a9c64f600c7cbe
  - "crates/sui-core/src/checkpoints/mod.rs:641"
  - "crates/sui-core/src/checkpoints/mod.rs:397"
  - "crates/sui-core/src/checkpoints/mod.rs:1104"
  - "crates/sui-core/src/checkpoints/mod.rs:979"
bug_class: checkpoint-execution-invariant
impact_type:
  - state-integrity
confidence: medium
tags:
  - blockchain-core
  - checkpointing
  - validator-logic
  - invariant-enforcement
  - state-integrity
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch adds explicit checkpoint/execution consistency checks in Sui checkpointing code, rejecting checkpoint contents that include unexecuted transactions. The evidence supports an invariant-enforcement or correctness-hardening change, but it does not establish a concrete vulnerability, attacker-controlled path, exploitability, asset impact, signature forgery, or consensus split.

## Observed Patch Facts

1. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `let next_sequence_number = self.next_checkpoint();` with `// We only attempt to reconstruct if we have a local proposal.`.

2. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `// Sign the new checkpoint` with `// Ensure we have processed all transactions contained in this checkpoint.`.

3. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `let already_in_checkpoint_tx =` with `// Check we are not re-proposing the same transactions that are already in a`.

4. In `crates/sui-core/src/checkpoints/mod.rs`, the patch replaces `let batch = self.transactions_to_checkpoint.batch();` with `// Ensure we have processed all transactions contained in this checkpoint.`.

## Project Context

The changed code sits primarily in `crates/sui-core/src/checkpoints`, `crates/sui-core/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/sui-core/src/checkpoints/reconstruction.rs`, `crates/sui-core/src/checkpoints/proposal.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/sui-core/src/authority/authority_store.rs`, `crates/sui-core/src/authority.rs`. The strongest project-level identifiers around this patch are `transactions`, `SuiError::from`, `checkpoint`, and `have`. Nearby tests or test-like files include `crates/sui-core/src/checkpoints/tests/checkpoint_tests.rs`, `crates/sui-core/src/unit_tests/batch_tests.rs`.

## Before/After Behavior

Before the patch, the shown checkpoint update/handling paths could proceed without the newly added `all_checkpoint_transactions_executed` guard. After the patch, `handle_internal_set_checkpoint` and `update_new_checkpoint` reject checkpoint contents or transaction lists if any listed transaction has not been executed. The reconstruction path also now returns early unless a local proposal exists. Comments in processed-transaction bookkeeping were updated to reflect the assumption that accepted checkpoints contain only processed transactions.

# Root Cause

Checkpointing code did not consistently show an explicit precondition check tying checkpoint contents to local execution state before advancing checkpoint-related state. The provided evidence does not prove this was exploitable; it only shows the invariant was made explicit in selected paths.

## Walkthrough

1. A checkpoint handling or update path receives checkpoint contents or a transaction list.

2. The patched code calls `all_checkpoint_transactions_executed` before continuing in the shown paths.

3. If the check fails, the operation returns `SuiError::from("Checkpoint contains unexecuted transactions.")`.

4. Checkpoint reconstruction is additionally skipped when there is no local proposal.

5. The updated comments document the intended invariant that finalized checkpoints should only contain processed transactions.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/sui-core/src/checkpoints/mod.rs | 397 | Before signing or handling a checkpoint, checks `all_checkpoint_transactions_executed(contents)` and returns an error if the checkpoint contains unexecuted transactions. |
| crates/sui-core/src/checkpoints/mod.rs | 641 | Checkpoint reconstruction is gated on having a local proposal and then attempts reconstruction with the expectation that checkpoint contents are validated before downstream processing. |
| crates/sui-core/src/checkpoints/mod.rs | 979 | `update_new_checkpoint` rejects transaction lists that are not fully executed before updating checkpoint state. |
| crates/sui-core/src/checkpoints/mod.rs | 1104 | Processed-transaction bookkeeping now relies on the invariant that finalized checkpoints only contain already processed transactions. |

## Code Snippets

## Snippet 1

Context: `crates/sui-core/src/checkpoints/mod.rs:641` (changes a consensus- or validator-sensitive branch)

Before
```rust
committee: &Committee,
    ) -> Result<bool, FragmentInternalError> {
        let next_sequence_number = self.next_checkpoint();
        let fragments: Vec<_> = self
```
After
```rust
committee: &Committee,
    ) -> Result<bool, FragmentInternalError> {
        // We only attempt to reconstruct if we have a local proposal.
        // By limiting reconstruction to when we have proposals we are
        // sure that we delay doing work to when it is needed.
        if self.get_locals().current_proposal.is_none() {
            return Ok(false);
        }
```

## Snippet 2

Context: `crates/sui-core/src/checkpoints/mod.rs:397` (changes a consensus- or validator-sensitive branch)

Before
```rust
);

        // Sign the new checkpoint
        let signed_checkpoint = AuthenticatedCheckpoint::Signed(
```
After
```rust
);

        // Ensure we have processed all transactions contained in this checkpoint.
        if !self.all_checkpoint_transactions_executed(contents)? {
            return Err(SuiError::from(
                "Checkpoint contains unexecuted transactions.",
            ));
        }
```

## Snippet 3

Context: `crates/sui-core/src/checkpoints/mod.rs:1104` (changes a consensus- or validator-sensitive branch)

Before
```rust
let batch = self.transactions_to_checkpoint.batch();

        let already_in_checkpoint_tx =
            transactions
                .iter()
                .zip(&in_checkpoint)
                .filter_map(
                    |((_seq, tx), in_chk)| {
```
After
```rust
let batch = self.transactions_to_checkpoint.batch();

        // Check we are not re-proposing the same transactions that are already in a
        // final checkpoint. This should not be possible since we only accept (sign /
        // record) a checkpoint if we have already processed all transactions within.
        let already_in_checkpoint_tx = transactions
            .iter()
            .zip(&in_checkpoint)
```

## Snippet 4

Context: `crates/sui-core/src/checkpoints/mod.rs:979` (changes a consensus- or validator-sensitive branch)

Before
```rust
transactions: &[ExecutionDigests],
    ) -> Result<(), SuiError> {
        let batch = self.transactions_to_checkpoint.batch();
        self.update_new_checkpoint_inner(seq, transactions, batch)?;
```
After
```rust
transactions: &[ExecutionDigests],
    ) -> Result<(), SuiError> {
        // Ensure we have processed all transactions contained in this checkpoint.
        if !self.all_checkpoint_transactions_executed(&CheckpointContents::new(
            transactions.iter().cloned(),
        ))? {
            return Err(SuiError::from(
                "Checkpoint contains unexecuted transactions.",
```

# Fix Pattern

Add precondition guards at checkpoint state-transition boundaries to reject checkpoint contents that are not fully reflected in local execution state.

## How It Was Fixed

The patch adds `all_checkpoint_transactions_executed` checks in `crates/sui-core/src/checkpoints/mod.rs` before internal checkpoint handling and before `update_new_checkpoint` updates checkpoint state. It also gates checkpoint reconstruction on the presence of a local proposal and updates comments around processed-transaction bookkeeping.

# Why It Matters

1. Keeps checkpoint metadata aligned with locally executed transaction state.

2. Avoids recording checkpoint state for transactions not yet processed locally.

3. Touches consensus/checkpointing-adjacent logic, but security impact is not demonstrated by the supplied evidence.

# Evidence Notes

Grounded evidence is limited to changed hunks in `crates/sui-core/src/checkpoints/mod.rs` around `handle_internal_set_checkpoint`, `attempt_to_construct_checkpoint`, `update_new_checkpoint`, and processed-transaction bookkeeping. The commit subject and comments support a checkpoint/execution invariant claim. They do not prove a vulnerability thesis or attacker impact, so the stronger `likely security-hardening` classification is not justified. Protocol security invariant: Checkpoint contents should not be accepted or recorded ahead of local transaction execution state: every transaction listed in a checkpoint should already be locally executed or processed before checkpoint state advances. Verification notes: No concrete attacker-controlled input path is proven by the patch evidence. No proof of remote exploitability is shown. No proof of asset theft, unauthorized transaction execution, or signature forgery is shown. No proof of a consensus split is shown, only a checkpoint/execution consistency risk. The evidence supports invariant enforcement in checkpointing, not a broad transaction-processing vulnerability. No concrete attacker-controlled input path is shown. No exploit scenario is established. No asset theft, unauthorized execution, signature forgery, or consensus split is proven. Tests were changed, but the provided evidence does not show a security regression test. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `checkpoint-execution-invariant`
Final impact type: `state-integrity`
Final confidence: `medium`
Final tags: `blockchain-core, checkpointing, validator-logic, invariant-enforcement, state-integrity`

The supplied patch evidence supports keeping this as security-hardening, not a concrete security-fix. The change adds explicit guards in checkpoint signing/acceptance/update paths to reject checkpoints containing unexecuted transactions, which tightens a security-sensitive blockchain consensus/checkpointing invariant. However, the evidence does not prove an attacker-controlled path, exploitability, or a realized consensus/state compromise, so stronger vulnerability claims should be avoided.

## Security Evidence

1. Checkpoint handling now rejects contents when all_checkpoint_transactions_executed returns false.
2. Checkpoint update now rejects transaction lists that include unexecuted transactions.
3. The check is placed before signing or recording checkpoint state in validator/checkpointing logic.
4. Comments state the intended invariant that accepted signed/recorded checkpoints contain only processed transactions.

## Missing Evidence

1. No attacker-controlled input path is demonstrated.
2. No exploit scenario or proof of remote triggerability is shown.
3. No concrete asset loss, unauthorized transaction execution, signature forgery, or consensus split is proven.
4. No security advisory, CVE, or explicitly security-labeled regression test is provided.

## Claim Boundaries

1. Classify as invariant hardening in checkpointing logic, not as a proven exploitable vulnerability.
2. Do not claim theft, forgery, or unauthorized execution from the supplied patch alone.
3. Do not claim a demonstrated consensus split; only a checkpoint/execution consistency risk is supported.
4. The reconstruction gating change appears more like work avoidance or correctness unless tied to the execution invariant.
