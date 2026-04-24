# Root-Cause Card

## Metadata

- ID: `optimism-2026-04-22-optimism-transaction-processing-052c1d65dc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-consensus-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: A post-exec 0x7D transaction must be rejected unless the executor is in an SDM mode that produces or verifies it, and any produced SDM refund must not exceed the transaction's raw gas used.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: malformed-payload-acceptance
- Secondary impact: consensus-divergence-risk

## Short Reusable Lesson

- A post-exec 0x7D transaction must be rejected unless the executor is in an SDM mode that produces or verifies it, and any produced SDM refund must not exceed the transaction's raw gas used. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
