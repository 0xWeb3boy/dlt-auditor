# Root-Cause Card

## Metadata

- ID: `optimism-2025-12-03-optimism-consensus-a52de0ddea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-invariant-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: After the L2 safe head, a span batch should not yield or validate a singular batch whose L1 origin number is older than the safe head's L1 origin; if extraction fails, the derivation path should discard that span-batch state rather than continue with ambiguous state.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: consensus-integrity-risk
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- After the L2 safe head, a span batch should not yield or validate a singular batch whose L1 origin number is older than the safe head's L1 origin; if extraction fails, the derivation path should discard that span-batch state rather than continue with ambiguous state. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
