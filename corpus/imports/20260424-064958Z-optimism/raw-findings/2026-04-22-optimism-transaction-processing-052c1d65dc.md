---
case_id: case_20260422_052c1d65dc
project: optimism
domain: infrastructure
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: transaction-processing
source_quality: medium
date: 2026-04-22
source_refs:
  - git:052c1d65dc068a36d48627810af04b3aaa865109
  - "rust/alloy-op-evm/src/block/mod.rs:681"
  - "rust/alloy-op-evm/src/block/mod.rs:734"
  - "rust/alloy-op-evm/src/post_exec/inspector.rs:16"
  - "rust/alloy-op-evm/src/post_exec/inspector.rs:212"
bug_class: missing-consensus-validation
impact_type:
  - malformed-payload-acceptance
  - consensus-divergence-risk
confidence: medium
tags:
  - consensus
  - validation
  - block-execution
  - post-exec
  - hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supplied evidence supports a security-relevant validation fix in the SDM post-exec path. The patch adds fail-closed checks so malformed post-exec transactions are rejected when SDM is disabled or invalid, and impossible refund values are rejected before SDM gas metadata is emitted. The evidence is strong enough to treat this as a likely security fix, but not strong enough to prove a broader exploit story beyond malformed payload acceptance and producer/verifier mismatch.

## Observed Patch Facts

1. In `rust/alloy-op-evm/src/block/mod.rs`, the patch replaces `// Validates that no Verify payload entry targets this tx index; refund is always 0.` with `// A 0x7D tx is only legitimate when the executor is wired to either produce or`.

2. In `rust/alloy-op-evm/src/block/mod.rs`, the patch replaces `(self.take_last_post_exec_tx_result)(&mut self.evm).refund_total` with `let refund = (self.take_last_post_exec_tx_result)(&mut self.evm).refund_total;`.

3. In `rust/alloy-op-evm/src/post_exec/inspector.rs`, the patch replaces `/// Classification for the currently executing transaction.` with `// EIP-2929 repeat-access savings. SDM refunds a tx whenever it re-touches something...`.

4. In `rust/alloy-op-evm/src/post_exec/inspector.rs`, the patch replaces `self.current_tx.add_refund(if is_sstore { 2100 } else { 2000 });` with `self.current_tx.add_refund(if is_sstore {`.

## Project Context

The changed code sits primarily in `rust/alloy-op-evm/src/block`, `rust/alloy-op-evm/src`, `rust/alloy-op-evm/src/post_exec`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `rust/alloy-op-evm/src/post_exec/mod.rs`, `rust/alloy-op-evm/src/block/receipt_builder.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `rust/alloy-op-evm/src/lib.rs`, `rust/alloy-op-evm/src/post_exec/mod.rs`. The strongest project-level identifiers around this patch are `block`, `refund`, `that`, and `PostExecMode`.

## Before/After Behavior

Before the patch, the shown `is_post_exec` path in `execute_transaction_without_commit` did not reject post-exec transactions when `PostExecMode` was `Disabled` or `Invalid`, and the Produce-mode refund path accepted `refund_total` without checking it against `raw_gas_used`. After the patch, the executor returns an error for unexpected post-exec transactions when SDM is not active, and it returns an error if a produced refund exceeds raw gas used. The inspector constant changes document refund math but do not independently show a separate behavioral fix.

# Root Cause

The root cause was missing fail-closed validation at the SDM post-exec boundary in block execution: the executor did not enforce that post-exec transactions were only valid in the right mode, and it did not enforce that produced refund metadata stayed within a basic gas-usage bound.

## Walkthrough

1. `execute_transaction_without_commit` identifies post-exec transactions with `is_post_exec`, placing the change on the transaction execution path.

2. In the pre-change branch, the visible code only called `verifier_post_exec_refund_for_tx(..., 0)?;` and did not show rejection for `PostExecMode::Disabled` or `Invalid`.

3. The patch adds an explicit mode check and returns `invalid_post_exec_payload(...)` when SDM is not active for the block.

4. A later hunk computes `raw_gas_used` and, in `PostExecMode::Produce`, now rejects `refund_total` values greater than `raw_gas_used`.

5. The added comment states the reason for the refund check: otherwise the builder could emit an `SDMGasEntry` that a verifier rejects at pre-execution.

6. The `inspector.rs` changes replace literal refund values with named EIP-2929-derived constants, which supports readability and auditability but is not the primary evidence of the vulnerability.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| rust/alloy-op-evm/src/block/mod.rs | 639 | block execution gate that now rejects post-exec 0x7D transactions when SDM is disabled or invalid |
| rust/alloy-op-evm/src/block/mod.rs | 728 | post-exec refund accounting path that now rejects refunds larger than raw gas used before emitting SDM gas data |
| rust/alloy-op-evm/src/post_exec/inspector.rs | 202 | warming-refund attribution logic whose constants are clarified, supporting the refund-accounting invariant but not introducing a separate proven security fix |

## Code Snippets

## Snippet 1

Context: `rust/alloy-op-evm/src/block/mod.rs:681` (changes a sensitive control or state-update path)

Before
```rust
if is_post_exec {
            // Validates that no Verify payload entry targets this tx index; refund is always 0.
            self.verifier_post_exec_refund_for_tx(tx_index, false, true, 0)?;
```
After
```rust
if is_post_exec {
            // A 0x7D tx is only legitimate when the executor is wired to either produce or
            // verify it. In Disabled mode the feature is off, so a 0x7D tx in the block is a
            // malformed block we must reject — silently short-circuiting would let a producer
            // ship arbitrary refund payloads that followers never validate. Invalid mode is
            // already caught in `apply_pre_execution_changes`; this arm is defense in depth.
            if matches!(self.post_exec_mode, PostExecMode::Disabled | PostExecMode::Invalid) {
```

## Snippet 2

Context: `rust/alloy-op-evm/src/block/mod.rs:734` (changes a sensitive control or state-update path)

Before
```rust
let post_exec_refund = match &self.post_exec_mode {
            PostExecMode::Produce => {
                (self.take_last_post_exec_tx_result)(&mut self.evm).refund_total
            }
            PostExecMode::Verify(_) => {
```
After
```rust
let post_exec_refund = match &self.post_exec_mode {
            PostExecMode::Produce => {
                let refund = (self.take_last_post_exec_tx_result)(&mut self.evm).refund_total;
                // The inspector's accumulated refund must never exceed the tx's raw gas. If
                // it does, we'd emit an `SDMGasEntry` that any honest verifier would reject
                // at pre-execution ("payload refund exceeds raw gas used"), so the sequencer
                // would ship a block it can't verify itself. Fail here with a loud error
                // instead of letting `saturating_sub` mask the discrepancy.
```

## Snippet 3

Context: `rust/alloy-op-evm/src/post_exec/inspector.rs:16` (changes aggregate state or economic accounting)

Before
```rust
};

/// Classification for the currently executing transaction.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
```
After
```rust
};

// EIP-2929 repeat-access savings. SDM refunds a tx whenever it re-touches something a prior
// tx in the same block already warmed, since the EVM charges the warm (cheap) fee but the
// block-level "real" cost was already paid by that prior tx.
//
// Values are derived from EIP-2929's cold/warm cost pairs:
//   COLD_ACCOUNT_ACCESS_COST (2600) - WARM_STORAGE_READ_COST (100) = 2500
```

## Snippet 4

Context: `rust/alloy-op-evm/src/post_exec/inspector.rs:212` (changes a sensitive control or state-update path)

Before
```rust
self.warmed_slots.contains(&(address, slot))
        {
            self.current_tx.add_refund(if is_sstore { 2100 } else { 2000 });
        }
```
After
```rust
self.warmed_slots.contains(&(address, slot))
        {
            self.current_tx.add_refund(if is_sstore {
                SSTORE_REWARM_REFUND
            } else {
                SLOAD_REWARM_REFUND
            });
        }
```

# Fix Pattern

Add explicit mode-gating and numeric invariant checks at the point where post-exec transactions and refund metadata are accepted or produced, so malformed inputs fail immediately instead of being silently tolerated.

## How It Was Fixed

The fix adds two direct validations in `rust/alloy-op-evm/src/block/mod.rs`: reject post-exec `0x7D` transactions when `PostExecMode` is `Disabled` or `Invalid`, and reject Produce-mode refunds larger than `raw_gas_used`. The `rust/alloy-op-evm/src/post_exec/inspector.rs` change only replaces magic numbers with named EIP-2929-based constants and should be treated as supporting cleanup/documentation.

# Why It Matters

1. Prevents silent acceptance of post-exec transactions when SDM is not active.

2. Reduces the risk of producer and verifier disagreement on post-exec gas metadata.

3. Turns malformed payload conditions into explicit execution failures.

4. The changed path is consensus/validation sensitive, so missing checks are higher impact than ordinary correctness bugs.

# Evidence Notes

The strongest evidence is the pair of new error paths in `rust/alloy-op-evm/src/block/mod.rs`, together with commit text and inline comments stating the prior outcomes: silent acceptance of a post-exec payload without validation, and production of refund metadata that a verifier would reject. The evidence does not show who can supply such malformed inputs or prove fund loss, and the inspector constant renaming plus constructor-signature restoration are not independently security-significant. Protocol security invariant: A post-exec 0x7D transaction must be rejected unless the executor is in an SDM mode that produces or verifies it, and any produced SDM refund must not exceed the transaction's raw gas used. Verification notes: The patch does not prove a remotely exploitable attack path or chain-wide compromise. It does not show who can inject malformed 0x7D transactions; it only shows nodes must reject them instead of silently accepting them. The over-refund case is shown as an invalid payload-production scenario, not proof of fund loss or successful gas manipulation on an accepted block. The constant renaming and `OpBuilderConfig` API restoration are not independently evidenced as security-relevant. The security claim is supported mainly by the added guards and author comments, not by a full end-to-end exploit trace. The evidence establishes malformed payload acceptance/rejection mismatch more clearly than any broader attacker model. The inspector constant renaming should not be counted as a separate vulnerability fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `missing-consensus-validation`
Final impact type: `malformed-payload-acceptance, consensus-divergence-risk`
Final confidence: `medium`
Final tags: `consensus, validation, block-execution, post-exec, hardening`

The patch is in a consensus- and validator-sensitive execution path and adds explicit fail-closed checks for malformed post-exec transactions and impossible refund values. The commit text and inline comments state that the old behavior could silently accept data that was never validated or produce metadata that honest verifiers would reject, which supports treating this as security hardening. The evidence does not, however, prove a concrete attacker-triggerable exploit or show accepted malicious state transitions on chain, so it is better retained as hardening rather than a confirmed security bug fix.

## Security Evidence

1. Adds an error path that rejects post-exec 0x7D transactions when SDM is Disabled or Invalid.
2. Inline comment says the prior behavior could silently accept refund payloads that followers never validate.
3. Adds an error path when produced refund exceeds raw gas used instead of masking it with saturating subtraction.
4. Commit message frames both changes as preventing malformed payload acceptance and producer/verifier mismatch in block validation.

## Missing Evidence

1. No proof that an external attacker, rather than a faulty or misconfigured producer, can trigger the bad states.
2. No end-to-end exploit or accepted malicious block is shown in the supplied patch evidence.
3. No evidence of fund theft, privilege escalation, or remote code execution.
4. The constant renaming in the inspector does not independently demonstrate a vulnerability fix.

## Claim Boundaries

1. Supported claim: this commit hardens consensus/validation behavior around malformed post-exec payload handling.
2. Not supported: a concrete exploitable security vulnerability with demonstrated attacker control.
3. Not supported: chain-wide compromise or economic loss beyond malformed payload rejection risk.
4. Do not count the EIP-2929 constant naming cleanup or constructor signature restoration as separate security fixes.
