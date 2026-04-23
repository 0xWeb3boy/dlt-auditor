# Root-Cause Card

## Metadata

- ID: `go-ethereum-2016-11-24-go-ethereum-storage-12d654a6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-revert-bug`
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

- The patch is best classified as a likely consensus-security fix in go-ethereum core/state. It makes account touch state explicit, journaled, and reversible so zero-value operations on empty accounts interact correctly with EIP158 clearing and Snapshot/Revert behavior. The evidence supports consensus-state compatibility risk, but not claims of theft, cryptographic failure, memory corruption, or proven exploitability.
