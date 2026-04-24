# Root-Cause Card

## Metadata

- ID: `sui-2023-02-27-sui-transaction-processing-f88a9a6cb6`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic-bounds`

## Violated Invariant

- Invariant: Protocol arithmetic must reject values outside the valid range before they can wrap, truncate, or distort state.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: committing security-sensitive protocol state

## Impact Pattern

- Primary impact: integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Protocol-controlled numeric values must be range checked before aggregation, conversion, or state commitment. The patch hardens Sui pay transaction accounting against u64 overflow when summing coin balances. The strongest supported claim is integer-overflow hardening in coin payment execution, not a proven exploit, denial of service, theft, or consensus failure.
