---
case_id: case_20231223_8fb6ed9cc
project: reth
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: medium
date: 2023-12-23
source_refs:
  - git:8fb6ed9cc5c1f4fbad48036aa018676f2c32cb84
  - "crates/consensus/common/src/validation.rs:93"
bug_class: incorrect-fork-gating
impact_type:
  - improper-transaction-validation
confidence: medium
tags:
  - blockchain-core
  - consensus
  - transaction-validation
  - fork-gating
  - eip-1559
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch corrects the hardfork check used in the `Transaction::Eip1559` validation path, changing it from `Berlin` to `London` in a consensus validation function. The evidence supports a protocol-rule mismatch in transaction validation, but it does not establish a concrete security impact beyond incorrect gating.

## Observed Patch Facts

1. In `crates/consensus/common/src/validation.rs`, the patch replaces `if !chain_spec.fork(Hardfork::Berlin).active_at_block(at_block_number) {` with `if !chain_spec.fork(Hardfork::London).active_at_block(at_block_number) {`.

## Project Context

The changed code sits primarily in `crates/consensus/common/src`, `crates/consensus/common`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `crates/consensus/common/src/calc.rs`, `crates/consensus/common/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `crates/consensus/common/src/calc.rs`. The strongest project-level identifiers around this patch are `Hardfork::Berlin`, `Hardfork::London`, `chain_spec`, and `fork`.

## Before/After Behavior

Before the patch, the EIP-1559 validation branch returned `Eip1559Disabled` only when `Berlin` was inactive, so the branch was keyed to the wrong fork name. After the patch, the same branch checks `London`, aligning the rejection condition with the intended EIP-1559 activation fork shown by the surrounding code and comments.

# Root Cause

A validator branch for `Transaction::Eip1559` referenced the wrong hardfork constant, using `Hardfork::Berlin` instead of `Hardfork::London` when deciding whether the transaction type was enabled.

## Walkthrough

1. The only code change is inside `validate_transaction_regarding_header` in `crates/consensus/common/src/validation.rs`.

2. In the `Transaction::Eip1559` branch, the pre-fix code checked `chain_spec.fork(Hardfork::Berlin).active_at_block(at_block_number)`.

3. That branch returns `InvalidTransactionError::Eip1559Disabled` when the selected fork is not active.

4. The patch changes the selected fork from `Berlin` to `London` and leaves the rest of the logic unchanged.

5. The surrounding function context shows similar per-transaction-type fork checks, including `Eip2930` gated on `Berlin`, which supports that this was a fork-selection bug rather than a broader redesign.

6. The evidence shows a correctness fix in consensus-related validation, but does not show whether any invalid transaction could actually be accepted in practice by the full system or whether other checks already prevented that.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| crates/consensus/common/src/validation.rs | 65 | Consensus transaction validation entrypoint that dispatches per-transaction-type fork checks against the current block number |
| crates/consensus/common/src/validation.rs | 93 | EIP-1559-specific activation gate; corrected from Berlin to London to enforce the proper protocol enablement boundary |

## Code Snippets

## Snippet 1

Context: `crates/consensus/common/src/validation.rs:93` (changes a consensus- or validator-sensitive branch)

Before
```rust
}) => {
            // EIP-1559: Fee market change for ETH 1.0 chain https://eips.ethereum.org/EIPS/eip-1559
            if !chain_spec.fork(Hardfork::Berlin).active_at_block(at_block_number) {
                return Err(InvalidTransactionError::Eip1559Disabled.into())
            }
```
After
```rust
}) => {
            // EIP-1559: Fee market change for ETH 1.0 chain https://eips.ethereum.org/EIPS/eip-1559
            if !chain_spec.fork(Hardfork::London).active_at_block(at_block_number) {
                return Err(InvalidTransactionError::Eip1559Disabled.into())
            }
```

# Fix Pattern

Replace an incorrect protocol-version gate with the hardfork condition that matches the transaction type being validated.

## How It Was Fixed

The fix is a one-line change in the EIP-1559 validation branch: `chain_spec.fork(Hardfork::London).active_at_block(at_block_number)` is now used instead of `Hardfork::Berlin`, so the existing `Eip1559Disabled` path is triggered against the corrected fork boundary.

# Why It Matters

1. Consensus validation depends on matching protocol rules to the correct fork boundary.

2. Using the wrong fork constant can make validation behavior inconsistent with the intended protocol mapping.

3. The provided evidence shows a real validation bug, even though downstream impact is not demonstrated.

# Evidence Notes

Grounded evidence is limited to a single-line diff and the surrounding function context. The strongest supported claim is that the EIP-1559 branch previously used the wrong fork constant and now uses the corrected one. The evidence does not prove exploitability, consensus divergence, block acceptance impact, or the absence of compensating checks elsewhere. Protocol security invariant: A typed transaction should only be accepted once the hardfork that enables that transaction type is active at the block being validated. Verification notes: The patch does not by itself prove remote exploitability. The patch does not prove a mainnet consensus split actually occurred. The patch does not show whether other validation layers also rejected these transactions. The evidence supports a fork-gating validation bug, not fund theft or privilege escalation. The exact runtime impact may differ between block import, mempool admission, and other callers of this validator. Confirmed from the diff that only the fork constant changed: `Berlin` to `London`. Confirmed from surrounding context that the change is inside transaction validation logic, not test or refactor code. Not established from the provided evidence whether this path is the sole enforcement point for EIP-1559 enablement. Not established from the provided evidence whether the bug was reachable on production chains or caused any observed security failure. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `incorrect-fork-gating`
Final impact type: `improper-transaction-validation`
Final confidence: `medium`
Final tags: `blockchain-core, consensus, transaction-validation, fork-gating, eip-1559`

The patch changes the EIP-1559 transaction gate in consensus validation from the Berlin fork to the London fork, which is the correct activation boundary for that transaction type. In a blockchain client, incorrect fork gating in consensus-facing validation is security-sensitive because it can admit protocol features before activation or apply the wrong rules at a boundary. The evidence does not prove an exploitable consensus split or show that this was the only enforcement point, so this is better treated as security hardening rather than a confirmed security bug fix.

## Security Evidence

1. The changed code is in `validate_transaction_regarding_header`, a consensus validation function.
2. The patch corrects the activation check for `Transaction::Eip1559` from `Hardfork::Berlin` to `Hardfork::London`.
3. Before the fix, the code could treat EIP-1559 transactions as enabled at the wrong fork boundary.
4. The function returns `Eip1559Disabled` based on this fork check, so the condition directly controls acceptance or rejection of that transaction type.

## Missing Evidence

1. No proof that this function is the sole enforcement point for EIP-1559 enablement.
2. No evidence of an observed exploit, chain split, or invalid block acceptance.
3. No test or runtime evidence showing the exact impact on mainnet or production deployments.
4. No evidence about mempool versus block-import reachability or whether compensating checks existed elsewhere.

## Claim Boundaries

1. Supported: the patch fixes an incorrect protocol-version gate for EIP-1559 transaction validation.
2. Supported: the pre-fix code used a too-early fork boundary for enabling EIP-1559 logic.
3. Not supported: a concrete consensus failure, exploit, or fund-impact scenario occurred.
4. Not supported: this was definitely a remotely exploitable vulnerability rather than a defensive correctness fix.
