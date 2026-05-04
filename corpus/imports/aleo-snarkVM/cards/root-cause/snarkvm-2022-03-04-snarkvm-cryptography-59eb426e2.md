# Root-Cause Card

## Metadata

- ID: `snarkvm-2022-03-04-snarkvm-cryptography-59eb426e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unchecked-tree-index-capacity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `index-capacity-bounds`

## Violated Invariant

- Invariant: State tree and program index mutations must reject batches that exceed the addressable index range before mutating canonical state.

## Trust Boundary

- Boundary: batch state update -> Merkle or program index storage

## Attack Surface

- Entrypoint type: state-update-validation
- Sensitive sink: program function index and ledger block-hash tree insertion

## Impact Pattern

- Primary impact: availability and validation hardening
- Secondary impact: state integrity if an overflow could encode an incorrect index

## Short Reusable Lesson

- Append-only authenticated data structures need pre-mutation capacity checks where the logical index crosses a smaller integer type.
