# Root-Cause Card

## Metadata

- ID: `optimism-2025-11-24-optimism-consensus-1210787f39`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `payload-derivation-filtering`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: When deriving a Holocene deposit-only payload, the OpPayloadAttributes used for block building should contain only deposit transactions; non-deposit transactions should be removed before those attributes are forwarded downstream.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: invalid-payload-construction
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- When deriving a Holocene deposit-only payload, the OpPayloadAttributes used for block building should contain only deposit transactions; non-deposit transactions should be removed before those attributes are forwarded downstream. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
