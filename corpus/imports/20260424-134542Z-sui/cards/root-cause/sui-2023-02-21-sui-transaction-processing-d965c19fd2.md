# Root-Cause Card

## Metadata

- ID: `sui-2023-02-21-sui-transaction-processing-d965c19fd2`
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

- Primary impact: asset-integrity
- Secondary impact: context-dependent

## Short Reusable Lesson

- Protocol-controlled numeric values must be range checked before aggregation, conversion, or state commitment. The patch fixes unchecked aggregation of pay transaction recipient amounts. Previously, check_total_coins() summed u64 amounts with amounts.iter().sum() before comparing the result to available coin value. The patch uses checked_add and returns TotalAmountOverflow if the aggregate exceeds u64.
