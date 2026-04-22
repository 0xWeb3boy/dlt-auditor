# Root-Cause Card

## Metadata

- ID: `scroll-2025-02-07-scroll-transaction-processing-794b92c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-compatibility-check`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `capability-gating`

## Violated Invariant

- Invariant: The coordinator should assign proving tasks only to provers that explicitly advertise compatibility with the task's required hard fork.

## Trust Boundary

- Boundary: `coordinator-scheduler->prover-task-assignment`

## Attack Surface

- Entrypoint type: `registration-path`
- Sensitive sink: `dispatch of hard-fork-specific proving work to a selected prover`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `denial-of-service`

## Short Reusable Lesson

- The coordinator should assign proving tasks only to provers that explicitly advertise compatibility with the task's required hard fork. The patch re-enables a fork-compatibility check in three prover-task assignment paths. The evidence shows the coordinator previously had this guard commented out and now rejects assignment when the prover does not advertise support for the task's required hard fork. That establishes a real correctness and safety check was restored, but the provided material does not prove a concrete security vulnerability or downstream acceptance of invalid proofs. The robust fix is to restore fail-closed hard-fork capability checks in every prover-task assignment path before dispatching chunk, batch, or bundle work.
