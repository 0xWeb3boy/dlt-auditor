# Root-Cause Card

## Metadata

- ID: `optimism-2023-10-26-optimism-transaction-processing-210492cdcb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-machine-atomicity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: The derivation pipeline should only advance the safe L2 head after an entire span batch has been processed successfully, and queued safe attributes must be checked against the in-progress pending safe head rather than the already-committed safe head.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: state-inconsistency
- Secondary impact: liveness

## Short Reusable Lesson

- The derivation pipeline should only advance the safe L2 head after an entire span batch has been processed successfully, and queued safe attributes must be checked against the in-progress pending safe head rather than the already-committed safe head. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
