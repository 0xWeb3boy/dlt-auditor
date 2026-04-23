# Root-Cause Card

## Metadata

- ID: `go-ethereum-2016-11-24-go-ethereum-storage-db567eb01`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-revert-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The evidence supports a consensus-relevant StateDB journaling fix, not a broader exploit primitive. The patch adds explicit journaling and undo behavior for touched empty accounts during zero-value balance handling, with a RIPEMD precompile exception described by the commit as Parity compatibility.
