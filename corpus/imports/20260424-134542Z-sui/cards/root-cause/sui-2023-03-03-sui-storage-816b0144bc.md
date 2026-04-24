# Root-Cause Card

## Metadata

- ID: `sui-2023-03-03-sui-storage-816b0144bc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-invariant-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Every state transition that consumes resources or changes balances must update the corresponding accounting state exactly once and within protocol bounds.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: committing fees, balances, or resource accounting state

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch is best characterized as SUI accounting hardening, not a proven vulnerability fix. The grounded evidence shows TemporaryStore::check_sui_conserved was adjusted to compute written-output SUI through TemporaryStore state instead of only the backing store, and supporting GetModule/ObjectStore trait implementations were.
