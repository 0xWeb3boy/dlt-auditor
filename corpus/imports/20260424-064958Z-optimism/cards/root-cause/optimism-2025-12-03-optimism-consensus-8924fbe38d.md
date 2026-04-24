# Root-Cause Card

## Metadata

- ID: `optimism-2025-12-03-optimism-consensus-8924fbe38d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: After the L2 safe head, a singular batch derived from a span batch must not use an L1 origin older than the safe head's L1 origin. If singular-batch extraction in that path fails, the pipeline should take the same drop-or-flush recovery path used for invalid span batches rather than propagating an inconsistent intermediate error.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: correctness-or-hardening
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- After the L2 safe head, a singular batch derived from a span batch must not use an L1 origin older than the safe head's L1 origin. If singular-batch extraction in that path fails, the pipeline should take the same drop-or-flush recovery path used for invalid span batches rather than propagating an inconsistent intermediate error. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce input-validation at the boundary and fail closed before state.
