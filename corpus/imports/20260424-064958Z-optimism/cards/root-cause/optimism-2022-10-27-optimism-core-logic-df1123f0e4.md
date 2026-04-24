# Root-Cause Card

## Metadata

- ID: `optimism-2022-10-27-optimism-core-logic-df1123f0e4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: L2 finalization should only advance from an L1 finalization signal that is monotonic and corresponds to L1 chain data the derivation pipeline has already processed on its current L1 view.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: integrity-risk
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- L2 finalization should only advance from an L1 finalization signal that is monotonic and corresponds to L1 chain data the derivation pipeline has already processed on its current L1 view. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
