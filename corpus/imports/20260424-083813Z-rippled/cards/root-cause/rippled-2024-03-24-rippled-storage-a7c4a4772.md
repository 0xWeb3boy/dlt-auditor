# Root-Cause Card

## Metadata

- ID: `rippled-2024-03-24-rippled-storage-a7c4a4772`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `amm-offer-overflow-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `numeric-bounds`

## Violated Invariant

- Invariant: Numeric protocol values must be range checked and rounded deterministically before they affect ledger accounting or eligibility decisions.

## Trust Boundary

- Boundary: validated ledger/history data -> persistent state or index storage

## Attack Surface

- Entrypoint type: state-storage-or-ledger-update-path
- Sensitive sink: persistent ledger state, object index, cache, or history consistency

## Impact Pattern

- Primary impact: state-integrity, economic-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch appears to fix incorrect handling of large synthetic AMM offers in rippled's payment AMM path.
