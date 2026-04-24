# Root-Cause Card

## Metadata

- ID: `optimism-2024-02-02-optimism-transaction-processing-e9172f60bb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `preimage-representation-confusion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `integrity-binding`

## Violated Invariant

- Invariant: If large preimages are uploaded to the oracle, the uploaded bytes and the reported size should refer to the same canonical raw preimage bytes, not an internal length-prefixed representation.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: data-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- If large preimages are uploaded to the oracle, the uploaded bytes and the reported size should refer to the same canonical raw preimage bytes, not an internal length-prefixed representation. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce integrity-binding at the boundary and fail closed before state, privilege, or consensus-visible output changes.
