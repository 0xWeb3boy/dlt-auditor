# Root-Cause Card

## Metadata

- ID: `scroll-2025-09-26-scroll-transaction-processing-9c8782fc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `integrity-check-missing`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `header-hash-consistency`

## Violated Invariant

- Invariant: Validium batch proving tasks should carry a canonical batch header whose recomputed hash matches the stored batch identity before proving proceeds.

## Trust Boundary

- Boundary: `coordinator-db-state->prover-task`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `batch proving task accepted into the validium proving pipeline`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Validium batch proving tasks should carry a canonical batch header whose recomputed hash matches the stored batch identity before proving proceeds. The provided evidence supports a validium-task correctness fix, not a proven vulnerability fix. The coordinator now explicitly constructs a validium batch header for batch tasks, and the prover now sanity-checks that the header's recomputed hash matches the stored hash. That is an internal integrity/correctness improvement in the proving pipeline, but the snippets do not establish external attacker control or a concrete security impact. The robust fix is to construct the validium batch header explicitly in the coordinator and reject tasks in the prover when the recomputed header hash differs from the stored batch identity.
