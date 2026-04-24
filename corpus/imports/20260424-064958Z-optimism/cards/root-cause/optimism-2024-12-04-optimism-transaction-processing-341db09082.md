# Root-Cause Card

## Metadata

- ID: `optimism-2024-12-04-optimism-transaction-processing-341db09082`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation-omission`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: An Optimism node must reject a child header whose base_fee_per_gas does not satisfy the fork-specific fee rule active for the parent context. Once Holocene rules apply at the parent timestamp, generic parent-based EIP-1559 validation alone is not sufficient for header admission.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: invalid-block-acceptance
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- An Optimism node must reject a child header whose base_fee_per_gas does not satisfy the fork-specific fee rule active for the parent context. Once Holocene rules apply at the parent timestamp, generic parent-based EIP-1559 validation alone is not sufficient for header admission. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
