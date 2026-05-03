---
case_id: case_20241004_cc8857336
project: movement
domain: blockchain-core
render_mode: mapper-drafter-skeptic
context_depth: deep
phase3_security_verdict: likely
phase3_validated_as: security-fix
phase3_keep_candidate: true
subsystem: p2p-networking
source_quality: medium
date: 2024-10-04
source_refs:
  - git:cc8857336818faf4488863902f95cb449ff565d6
  - "protocol-units/execution/opt-executor/src/transaction_pipe.rs:158"
bug_class: transaction-sequence-validation
impact_type:
  - denial-of-service
  - resource-exhaustion
confidence: medium
tags:
  - blockchain-core
  - transaction-admission
  - sequence-number-validation
  - denial-of-service
  - gas-dos
validation_status: completed
security_verdict: likely
validated_as: security-hardening
keep_in_security_corpus: true
---


# Summary

Commit cc8857336 changes TransactionPipe::has_invalid_sequence_number so the maximum acceptable transaction sequence number is computed from committed_sequence_number + TOO_NEW_TOLERANCE instead of max(used_sequence_number, committed_sequence_number) + TOO_NEW_TOLERANCE. The provided evidence supports a likely DoS-prevention fix in transaction admission, but does not show the full resource exhaustion path or the contents of the added gas_dos e2e file.

## Observed Patch Facts

1. In `protocol-units/execution/opt-executor/src/transaction_pipe.rs`, the patch replaces `let max_sequence_number =` with `let max_sequence_number = committed_sequence_number + TOO_NEW_TOLERANCE;`.

## Project Context

The changed code sits primarily in `protocol-units/execution/opt-executor/src`, `protocol-units/execution/opt-executor`, which anchors the finding in the `p2p-networking` area of the project. Historical context from `protocol-units/execution/opt-executor/src/service.rs`, `protocol-units/execution/opt-executor/src/lib.rs` was reviewed at the same commit to understand the surrounding types, RPC boundaries, and data flow. Deep identifier tracing also followed the touched subsystem into `protocol-units/execution/opt-executor/src/service.rs`, `protocol-units/execution/opt-executor/src/lib.rs`. The strongest project-level identifiers around this patch are `max_sequence_number`, `min_sequence_number`, `committed_sequence_number`, and `used_sequence_number`.

## Before/After Behavior

Before the patch, the too-new upper bound could be raised by used_sequence_number as well as committed_sequence_number. Because used_sequence_number is read from a local pool and defaults to the submitted transaction's sequence number when absent, the upper bound could be influenced by local or submitted sequence state rather than only committed account state. After the patch, the upper bound is committed_sequence_number + TOO_NEW_TOLERANCE, while the lower bound still uses max(used_sequence_number, committed_sequence_number).

# Root Cause

The validation logic used the same max(used_sequence_number, committed_sequence_number) base for both stale-sequence rejection and too-new rejection. That made the future acceptance ceiling depend on local used-sequence state, and possibly on the submitted transaction sequence number through the default path, instead of being anchored solely to committed account state.

## Walkthrough

1. A SignedTransaction is checked by TransactionPipe::has_invalid_sequence_number.

2. The function reads used_sequence_number from used_sequence_number_pool, defaulting to transaction.sequence_number() if no local value exists.

3. The function reads committed_sequence_number from the latest state checkpoint view.

4. The lower bound remains max(used_sequence_number, committed_sequence_number).

5. Before the fix, max_sequence_number was max(used_sequence_number, committed_sequence_number) + TOO_NEW_TOLERANCE.

6. That allowed local/default used-sequence state to raise the too-new threshold above committed state plus tolerance.

7. After the fix, max_sequence_number is committed_sequence_number + TOO_NEW_TOLERANCE.

8. The patch also adds logging for min_sequence_number, max_sequence_number, and transaction_sequence_number.

## Affected Code Paths

| File | Lines | Role |
| --- | --- | --- |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 139 | validates submitted transaction sequence numbers against committed account state and local used-sequence tracking |
| protocol-units/execution/opt-executor/src/transaction_pipe.rs | 158 | computes the maximum acceptable future sequence number for too-new rejection |
| networks/suzuka/suzuka-client/src/bin/e2e/gas_dos.rs | 1 | regression or scenario coverage for gas DoS behavior, based on changed file list |

## Code Snippets

## Snippet 1

Context: `protocol-units/execution/opt-executor/src/transaction_pipe.rs:158` (changes how canonical state is encoded, returned, or reconstructed)

Before
```rust
let min_sequence_number = used_sequence_number.max(committed_sequence_number);

		let max_sequence_number =
			used_sequence_number.max(committed_sequence_number) + TOO_NEW_TOLERANCE;

		if transaction.sequence_number() < min_sequence_number {
```
After
```rust
let min_sequence_number = used_sequence_number.max(committed_sequence_number);

		let max_sequence_number = committed_sequence_number + TOO_NEW_TOLERANCE;

		info!(
			"min_sequence_number: {:?} max_sequence_number: {:?} transaction_sequence_number {:?}",
			min_sequence_number,
			max_sequence_number,
```

# Fix Pattern

Separate lower-bound and upper-bound validation sources: use local used-sequence tracking for stale transaction detection, but anchor too-new sequence rejection to committed state.

## How It Was Fixed

In protocol-units/execution/opt-executor/src/transaction_pipe.rs, max_sequence_number was changed from used_sequence_number.max(committed_sequence_number) + TOO_NEW_TOLERANCE to committed_sequence_number + TOO_NEW_TOLERANCE. Logging was added for the computed bounds and transaction sequence number. The changed file list also includes an e2e gas_dos.rs file, but its contents are not provided.

# Why It Matters

1. Prevents local sequence tracking from widening the future-sequence admission window.

2. Makes too-new transaction rejection depend on committed account state.

3. Supports the commit's stated gas DoS prevention purpose.

4. Does not establish funds loss, signature bypass, or consensus failure.

# Evidence Notes

The strongest evidence is the direct calculation change in TransactionPipe::has_invalid_sequence_number. The heuristic baseline's p2p-networking and serialization interpretation is unsupported by the supplied diff and should be discarded. The commit subject and changed gas_dos.rs filename support security relevance, but the exact gas exhaustion mechanism, exploitability, and regression test behavior are not shown. Protocol security invariant: Transaction admission should bound too-new account sequence numbers against committed account state plus the configured tolerance. Local used-sequence or in-flight tracking may affect the lower bound for stale transactions, but should not expand the future-sequence ceiling beyond committed state. Verification notes: The patch does not prove funds loss, signature bypass, or consensus safety failure. The patch does not show the exact gas exhaustion mechanism or resource amplification factor. The evidence does not prove remote exploitability without the surrounding transaction submission path. The change is not evidence of a serialization, RPC representation, or p2p networking bug. Verified only from provided excerpts; no repository inspection was performed. Full too-new comparison code is implied by the function/comment context but not fully included in the excerpt. The added e2e gas_dos.rs file is listed but its contents are unavailable. Confidence is medium because the validation bug is clear, while the end-to-end DoS mechanics are not shown. Agent pipeline used separate mapper, drafter, and skeptic passes.

# Validation Notes

Validation status: `completed`
Security verdict: `likely`
Validated as: `security-hardening`
Keep in security corpus: `true`
Final bug class: `transaction-sequence-validation`
Final impact type: `denial-of-service, resource-exhaustion`
Final confidence: `medium`
Final tags: `blockchain-core, transaction-admission, sequence-number-validation, denial-of-service, gas-dos`

The supplied evidence supports retaining this as security hardening rather than a fully proven security fix. The patch tightens transaction admission by anchoring the too-new sequence-number ceiling to committed account state instead of allowing local used-sequence state, which may derive from the submitted transaction, to widen the acceptable range. The commit subject and listed gas_dos e2e file support DoS relevance, but the provided excerpt does not show the actual resource exhaustion path, rejection comparison, or test behavior.

## Security Evidence

1. Commit subject explicitly says "fix: gas dos prevention."
2. Implementation changes transaction sequence-number admission logic in TransactionPipe.
3. Before the patch, max_sequence_number used max(used_sequence_number, committed_sequence_number) + TOO_NEW_TOLERANCE.
4. After the patch, max_sequence_number is committed_sequence_number + TOO_NEW_TOLERANCE.
5. Provided context says used_sequence_number defaults to transaction.sequence_number(), which could let submitted or local state raise the too-new ceiling.
6. Changed file list includes an e2e gas_dos.rs regression/scenario file.

## Missing Evidence

1. Full has_invalid_sequence_number comparison and return behavior are not shown.
2. Contents of the added or updated gas_dos.rs test are not provided.
3. No concrete exploit flow, resource amplification, or remote submission path is shown.
4. No evidence proves consensus failure, funds loss, signature bypass, or client-view divergence.

## Claim Boundaries

1. Classify as transaction admission/sequence-number validation, not p2p networking or serialization/state representation.
2. Supported impact is conservative DoS/resource-exhaustion risk, not state consistency or client divergence.
3. The evidence supports security hardening with likely DoS relevance, but not a fully demonstrated exploitable vulnerability.
4. Do not claim more than anchoring too-new sequence rejection to committed account state.
