---
case_id: case_20230525_9d6c921b5f
project: solana
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: unclear
phase3_validated_as: unclear
phase3_keep_candidate: false
subsystem: transaction-processing
source_quality: high
date: 2023-05-25
source_refs:
  - git:9d6c921b5f73351702ba492cb3dee60d6e2db72f
  - "perf/src/sigverify.rs:1411"
  - "sdk/src/transaction/sanitized.rs:118"
  - "sdk/src/transaction/sanitized.rs:298"
bug_class: underconstrained-transaction-classification
impact_type:
  - validation-bypass-risk
confidence: medium
tags:
  - blockchain-core
  - transaction-processing
  - signature-validation
  - vote-transaction
  - classification-hardening
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

The patch tightens Solana sanitized transaction creation so automatic `is_simple_vote_tx` derivation requires `signatures.len() < 3` in addition to the existing legacy-message and single-instruction checks. The evidence supports a classification and validation hardening around simple vote transactions, but it does not establish an exploitable vulnerability or end-to-end security impact.

## Observed Patch Facts

1. In `perf/src/sigverify.rs`, the patch adds `// single legacy vote tx with extra (invalid) signature is not`.

2. In `sdk/src/transaction/sanitized.rs`, the patch replaces `if message.instructions().len() == 1 && matches!(message, SanitizedMessage::Legacy(_)) {` with `if signatures.len() < 3`.

3. In `sdk/src/transaction/sanitized.rs`, the patch adds `#[cfg(test)]`.

## Project Context

The changed code sits primarily in `perf/src`, `sdk/src/transaction`, `sdk/src`, which anchors the finding in the `transaction-processing` area of the project. Historical context from `sdk/src/transaction/mod.rs`, `sdk/src/transaction/error.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `sdk/src/transaction/mod.rs`, `sdk/src/transaction/versioned/sanitized.rs`. The strongest project-level identifiers around this patch are `message`, `SanitizedMessage::Legacy`, `Signature::default`, and `is_simple_vote_tx`.

## Before/After Behavior

Before the patch, `SanitizedTransaction::try_create` could derive `is_simple_vote_tx` for any legacy transaction with exactly one instruction before checking the vote program id, without first excluding transactions with three or more signatures. After the patch, that derivation only proceeds when `signatures.len() < 3`. Added tests cover sanitized transaction simple-vote behavior and a packet-level case where a legacy vote transaction with an appended default signature and `num_required_signatures = 3` returns `PacketError::InvalidSignatureLen`.

# Root Cause

The simple-vote classifier was under-constrained with respect to signature count. The supplied evidence shows the intended simple-vote shape permits one or two signatures, but the previous automatic classification guard did not encode that limit.

## Walkthrough

1. `SanitizedTransaction::try_create` sanitizes the incoming transaction, extracts `tx.signatures`, and converts the message into a `SanitizedMessage`.

2. When `is_simple_vote_tx` is not supplied, the function derives it from transaction structure.

3. Previously, derivation proceeded for legacy messages with exactly one instruction, regardless of whether the signature vector had three or more entries.

4. The patch adds `signatures.len() < 3` to that guard.

5. The added packet test constructs a legacy vote transaction with an extra default signature and requires the simple-vote packet path to return `InvalidSignatureLen`.

6. The evidence demonstrates stricter classification behavior, not a proven signature verification bypass or consensus failure.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| sdk/src/transaction/sanitized.rs | 118 | Derives `is_simple_vote_tx` during sanitized transaction creation and now rejects transactions with three or more signatures from the simple-vote classification. |
| perf/src/sigverify.rs | 1411 | Adds regression coverage that a legacy vote transaction with an extra invalid signature is rejected from the simple-vote packet path with `InvalidSignatureLen`. |
| sdk/src/transaction/sanitized.rs | 298 | Adds tests for sanitized transaction simple-vote creation behavior around signature counts. |

## Code Snippets

## Snippet 1

Context: `perf/src/sigverify.rs:1411` (changes signature or replay validation logic)

Before
```rust
assert!(!packet.meta().is_simple_vote_tx());
        }
    }
```
After
```rust
assert!(!packet.meta().is_simple_vote_tx());
        }

        // single legacy vote tx with extra (invalid) signature is not
        {
            let mut tx = new_test_vote_tx(&mut rng);
            tx.signatures.push(Signature::default());
            tx.message.header.num_required_signatures = 3;
```

## Snippet 2

Context: `sdk/src/transaction/sanitized.rs:118` (changes a sensitive control or state-update path)

Before
```rust
let is_simple_vote_tx = is_simple_vote_tx.unwrap_or_else(|| {
            if message.instructions().len() == 1 && matches!(message, SanitizedMessage::Legacy(_)) {
                let mut ix_iter = message.program_instructions_iter();
                ix_iter.next().map(|(program_id, _ix)| program_id)
```
After
```rust
let is_simple_vote_tx = is_simple_vote_tx.unwrap_or_else(|| {
            if signatures.len() < 3
                && message.instructions().len() == 1
                && matches!(message, SanitizedMessage::Legacy(_))
            {
                let mut ix_iter = message.program_instructions_iter();
                ix_iter.next().map(|(program_id, _ix)| program_id)
```

## Snippet 3

Context: `sdk/src/transaction/sanitized.rs:298` (changes signature or replay validation logic)

Before
```rust
}
}
```
After
```rust
}
}

#[cfg(test)]
#[allow(clippy::integer_arithmetic)]
mod tests {
    use {
        super::*,
```

# Fix Pattern

Add a missing structural precondition to a transaction fast-path classifier and cover the rejected shape with regression tests.

## How It Was Fixed

The fix added `signatures.len() < 3` to the automatic `is_simple_vote_tx` derivation in `sdk/src/transaction/sanitized.rs`. It also added tests in `sdk/src/transaction/sanitized.rs` and `perf/src/sigverify.rs` for simple-vote behavior around signature counts.

# Why It Matters

1. Touches transaction sanitization and vote transaction classification.

2. Prevents transactions with three or more signatures from being considered simple-vote candidates by this guard.

3. May reduce risk in a signature-sensitive fast path.

4. Provided evidence does not prove invalid signatures were accepted end to end.

# Evidence Notes

Grounded evidence is the changed guard in `sdk/src/transaction/sanitized.rs` and added regression coverage in `perf/src/sigverify.rs` and `sdk/src/transaction/sanitized.rs`. Claims about funds theft, privilege escalation, state corruption, consensus split, validator crash, or a demonstrated signature-verification bypass are unsupported by the supplied input. The mapper's `likely` security verdict and `keep_in_security_corpus: true` are stronger than the evidence supports. Protocol security invariant: Automatic simple-vote classification should only apply to transactions matching the expected simple-vote structure, including a legacy message, one instruction, and a signature count consistent with simple votes having one or two signatures. Verification notes: The patch does not prove that invalid signatures were accepted as valid transactions end to end. The patch does not show funds theft, privilege escalation, or state corruption directly. The evidence does not establish a consensus split or validator crash scenario. The change may primarily harden fast-path classification rather than fix a demonstrated exploitable vulnerability. Confirmed by provided diff snippets: the runtime condition now includes `signatures.len() < 3`. Confirmed by provided test snippet: an extra-signature legacy vote transaction is expected to produce `InvalidSignatureLen`. No supplied evidence shows an exploit path or end-to-end acceptance of an invalid transaction. Classified as unclear security relevance rather than confirmed or likely security fix. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `underconstrained-transaction-classification`
Final impact type: `validation-bypass-risk`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-processing, signature-validation, vote-transaction, classification-hardening`

The supplied patch clearly adds a missing signature-count precondition to automatic simple-vote transaction classification and adds regression coverage for a legacy vote transaction with an extra invalid signature returning InvalidSignatureLen. The evidence supports security hardening in a signature-sensitive transaction path, but it does not prove an exploitable end-to-end vulnerability, state corruption, or consensus impact, so it should not be treated as a confirmed security fix.

## Security Evidence

1. SanitizedTransaction::try_create now requires signatures.len() < 3 before deriving is_simple_vote_tx.
2. The commit subject states simple votes should have 1 or 2 signatures during sanitized transaction creation.
3. A regression test constructs a legacy vote transaction with an extra default signature and expects InvalidSignatureLen.
4. The changed behavior is in transaction sanitization and vote transaction classification, which are security-sensitive in a blockchain validator context.

## Missing Evidence

1. No supplied evidence shows invalid signatures were accepted end to end before the patch.
2. No exploit path, consensus split, funds impact, or state corruption is demonstrated.
3. No downstream use of is_simple_vote_tx is shown proving a security boundary was bypassed.
4. The production diff shown is a classifier constraint, not a direct cryptographic verification fix.

## Claim Boundaries

1. Classify as security hardening, not a confirmed security fix.
2. Do not claim state corruption from the provided evidence.
3. Do not claim signature verification bypass beyond the observed invalid-signature-length rejection test.
4. The supported claim is limited to stricter simple-vote classification based on signature count.
