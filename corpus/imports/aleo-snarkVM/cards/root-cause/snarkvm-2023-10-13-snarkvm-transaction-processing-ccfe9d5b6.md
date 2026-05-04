# Root-Cause Card

## Metadata

- ID: `snarkvm-2023-10-13-snarkvm-transaction-processing-ccfe9d5b6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-integrity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `deterministic-finalization-binding`

## Violated Invariant

- Invariant: Stored finalization effects for rejected transactions must match deterministic VM recomputation before they are accepted into canonical state.

## Trust Boundary

- Boundary: block-provided rejected transaction data -> VM state transition validation

## Attack Surface

- Entrypoint type: block-validation
- Sensitive sink: fee finalization operations applied or accepted for rejected deploy/execute transactions

## Impact Pattern

- Primary impact: consensus state-transition integrity
- Secondary impact: fee accounting consistency

## Short Reusable Lesson

- Any serialized state effect supplied with a block should be treated as a claim and checked against deterministic recomputation.
