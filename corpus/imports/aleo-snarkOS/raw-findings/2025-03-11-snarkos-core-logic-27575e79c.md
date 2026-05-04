---
case_id: case_20250311_27575e79c
project: snarkos
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-hardening
phase3_keep_candidate: true
subsystem: core-logic
confidence: medium
source_quality: medium
date: 2025-03-11
source_refs:
  - git:27575e79c63cf6ffb9d215d629d163415f5d4b07
  - "node/sync/locators/src/block_locators.rs:196"
bug_class: integer-overflow-in-input-validation
impact_type:
  - protocol-validation-hardening
tags:
  - blockchain-core
  - sync
  - block-locators
  - validator-input
  - integer-overflow
  - input-validation
  - security-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The supported finding is overflow-safe input validation hardening in snarkOS block locator checks. The evidence does not support the heuristic baseline's access-control theory, nor does it prove a concrete exploit, consensus split, or state corruption impact.

## Observed Patch Facts

1. In `node/sync/locators/src/block_locators.rs`, the patch replaces `// That is, 'last_checkpoint_height + CHECKPOINT_INTERVAL'` with `// That is, we must have`.

## Project Context

The changed code sits primarily in `node/sync/locators/src`, `node/sync/locators`, which anchors the finding in the `core-logic` area of the project. Historical context from `node/sync/locators/src/lib.rs`, `node/sync/locators/LICENSE.md` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `node/sync/locators/src/lib.rs`, `node/sync/locators/LICENSE.md`. The strongest project-level identifiers around this patch are `last_checkpoint_height`, `that`, `last_recent_height`, and `block`.

## Before/After Behavior

Before the patch, `check_block_locators` checked the relationship between `last_checkpoint_height` and `last_recent_height` using `last_checkpoint_height + CHECKPOINT_INTERVAL <= last_recent_height`, with comments saying overflow was not a concern. After the patch, the comments state the fuller invariant and explicitly treat `last_checkpoint_height` as an untrusted value from a faulty validator, saying saturating addition is used for the boundary check.

# Root Cause

Validation arithmetic was performed on a height value that the fixed code documents as untrusted, while the old code assumed `u32` block heights would not approach the overflow boundary.

## Walkthrough

1. `check_block_locators` validates recent block locators and checkpoint locators, producing `last_recent_height` and `last_checkpoint_height`.

2. The function then checks that the last checkpoint height is correctly positioned relative to the last recent height and `CHECKPOINT_INTERVAL`.

3. Before the patch, the relevant condition used unchecked addition in `last_checkpoint_height + CHECKPOINT_INTERVAL`.

4. The old comments explicitly relied on an expectation that block heights would not run out of `u32` range.

5. The patch documents that `last_checkpoint_height` may be untrusted input from a faulty validator.

6. The patch states that saturating addition is used to avoid overflow in this validation path.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| node/sync/locators/src/block_locators.rs | 187 | validates recent block and checkpoint locator structure during sync |
| node/sync/locators/src/block_locators.rs | 196 | enforces relationship between last checkpoint height and last recent height using overflow-safe arithmetic |
| node/sync/locators/src/lib.rs | 15 | exports block locator validation module |

## Code Snippets

## Snippet 1

Context: `node/sync/locators/src/block_locators.rs:196` (changes a consensus- or validator-sensitive branch)

Before
```rust
// Ensure that `last_checkpoint_height` is
        // the largest multiple of `CHECKPOINT_INTERVAL` that does not exceed `last_recent_height`.
        // That is, `last_checkpoint_height + CHECKPOINT_INTERVAL`
        // must be greater than `last_recent_height`.
        // We do not worry about this addition overflowing,
        // because our use of `u32` for block heights implies that we do not expect to run out.
        if last_checkpoint_height + CHECKPOINT_INTERVAL <= last_recent_height {
            bail!(
```
After
```rust
// Ensure that `last_checkpoint_height` is
        // the largest multiple of `CHECKPOINT_INTERVAL` that does not exceed `last_recent_height`.
        // That is, we must have
        // `last_checkpoint_height <= last_recent_height < last_checkpoint_height + CHECKPOINT_INTERVAL`.
        // Although we do not expect to run out of `u32` for block heights,
        // `last_checkpoint_height` is an untrusted value that may come from a faulty validator,
        // and thus we use a saturating addition;
        // only a faulty validator would send block locators with such high block heights,
```

# Fix Pattern

Use overflow-safe arithmetic when validating protocol data derived from untrusted peers or validators, and make the full structural invariant explicit.

## How It Was Fixed

The validation around `last_checkpoint_height` and `last_recent_height` was updated to document the complete expected relationship and to avoid unchecked interval addition by using saturating arithmetic.

# Why It Matters

1. Block locator data participates in node synchronization.

2. Faulty validator input should not be able to trigger arithmetic edge-case behavior in validation.

3. The evidence supports hardening against malformed extreme heights.

4. The evidence does not establish authorization bypass, memory corruption, or a proven consensus failure.

# Evidence Notes

Primary evidence is the focused change in `node/sync/locators/src/block_locators.rs` around `check_block_locators`. The before snippet shows unchecked addition in the validation condition. The after snippet documents untrusted validator input and saturating addition. The provided evidence does not include enough detail to prove the exact runtime impact of the prior overflow or the full final condition, so confidence is medium rather than high. Protocol security invariant: Block locator validation during synchronization should treat peer or validator supplied height values as untrusted and enforce the checkpoint/recent-height relationship without arithmetic overflow. Verification notes: No authorization or access-control flaw is shown by the patch. No concrete remote exploit path is proven from the provided evidence. No consensus split or state corruption impact is proven. No memory-safety issue is shown; the project context forbids unsafe code. No evidence shows whether overflow would panic, wrap, or only reject valid data in the compiled configuration. No access-control claim is supported. No concrete exploit path is proven. No memory-safety issue is shown. No consensus split or state corruption impact is proven. Security relevance rests on untrusted validator input plus overflow-safe protocol validation. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `integer-overflow-in-input-validation`
Final impact type: `protocol-validation-hardening`
Final tags: `blockchain-core, sync, block-locators, validator-input, integer-overflow, input-validation, security-hardening`

The supplied evidence supports retaining this as security hardening, not as a concrete security fix. The patch concerns validation of block locator heights in a blockchain sync path, replaces an unchecked boundary calculation with overflow-aware handling according to the after-comment, and explicitly identifies the height as untrusted input that may come from a faulty validator. The evidence does not support the original access-control or privilege-misuse framing, nor does it prove exploitability, consensus failure, or state corruption.

## Security Evidence

1. Commit subject says a missing check was added and overflow was protected against.
2. Before code used `last_checkpoint_height + CHECKPOINT_INTERVAL` in a validation condition.
3. After comments state `last_checkpoint_height` is untrusted and may come from a faulty validator.
4. After comments state saturating addition is used for the validation boundary.
5. Changed function validates block locators used for node synchronization.

## Missing Evidence

1. The provided diff excerpt does not show the final replacement condition itself.
2. No tests or failure reproduction are provided.
3. No evidence shows whether the old overflow would panic, wrap, accept invalid locators, or only reject valid input.
4. No concrete remote exploit path is demonstrated.
5. No evidence proves consensus split, state corruption, or authorization impact.

## Claim Boundaries

1. Classify as overflow-safe validation hardening only.
2. Do not retain access-control or privilege-misuse claims.
3. Do not claim a confirmed exploitable vulnerability from this evidence alone.
4. Do not claim memory-safety impact; the provided context indicates unsafe code is forbidden.
5. Do not claim consensus failure or state corruption without additional evidence.
