# Root-Cause Card

## Metadata

- ID: `optimism-2025-10-23-optimism-transaction-processing-5f5e50fa73`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fork-activation-validation-gap`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Fork activation blocks with protocol-defined upgrade behavior should not also accept ordinary user transactions; fork-detection helpers and batch validation need to enforce the same rule for each scheduled fork.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: invalid-batch-acceptance
- Secondary impact: consensus-risk

## Short Reusable Lesson

- Fork activation blocks with protocol-defined upgrade behavior should not also accept ordinary user transactions; fork-detection helpers and batch validation need to enforce the same rule for each scheduled fork. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
