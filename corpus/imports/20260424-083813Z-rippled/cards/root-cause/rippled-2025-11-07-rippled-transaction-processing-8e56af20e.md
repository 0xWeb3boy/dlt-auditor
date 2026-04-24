# Root-Cause Card

## Metadata

- ID: `rippled-2025-11-07-rippled-transaction-processing-8e56af20e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `numeric-representability-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `numeric-bounds`

## Violated Invariant

- Invariant: Numeric protocol values must be range checked and rounded deterministically before they affect ledger accounting or eligibility decisions.

## Trust Boundary

- Boundary: untrusted transaction -> deterministic ledger state transition

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: ledger state, balance/reserve accounting, or transaction authorization outcome

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch separates Number validity from representability and adds explicit representability checks for vault aggregate fields.
