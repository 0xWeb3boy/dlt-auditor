# Root-Cause Card

## Metadata

- ID: `scroll-2023-08-18-scroll-transaction-processing-767a2cbf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-transition`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `terminal-state-enforcement`

## Violated Invariant

- Invariant: Once a proof task reaches a verified terminal state, later submissions must not downgrade or mutate the verified batch or chunk status.

## Trust Boundary

- Boundary: `prover-result->coordinator-state-machine`

## Attack Surface

- Entrypoint type: `proof-submission-handler`
- Sensitive sink: `coordinator updates to chunk and batch proving status in persistent state`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `stale-trust-state`

## Short Reusable Lesson

- Once a proof task reaches a verified terminal state, later submissions must not downgrade or mutate the verified batch or chunk status. The evidence shows a focused state-machine fix in the coordinator proof receiver: after a chunk or batch is already verified, the code now skips later chunk/batch-level status updates for all incoming statuses instead of only `ProvingTaskFailed`. That supports a post-verification integrity/correctness hardening claim. The provided diff does not establish an attacker-driven vulnerability, cryptographic bypass, or consensus-impacting exploit. The robust fix is to make the verified status terminal and short-circuit all later state transitions that would otherwise revisit chunk or batch status after success.
