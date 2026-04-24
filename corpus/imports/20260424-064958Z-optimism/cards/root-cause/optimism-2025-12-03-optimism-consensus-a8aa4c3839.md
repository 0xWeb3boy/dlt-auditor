# Root-Cause Card

## Metadata

- ID: `optimism-2025-12-03-optimism-consensus-a8aa4c3839`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: For post-safe-head processing, a singular batch derived from a span batch should not use an L1 origin older than the safe head's L1 origin, and singular-batch extraction failures should be handled as invalid/incomplete batch processing rather than a normal successful path.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: invalid-batch-acceptance
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- For post-safe-head processing, a singular batch derived from a span batch should not use an L1 origin older than the safe head's L1 origin, and singular-batch extraction failures should be handled as invalid/incomplete batch processing rather than a normal successful path. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
