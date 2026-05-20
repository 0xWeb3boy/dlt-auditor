# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-ceil-double-increment-32700`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-rounding-double-adjustment`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the second adjustment is guarded by a distinct unit conversion that does not change value.
- Pure presentation rounding is lower risk without settlement use.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Rounding upward by more than one step can overpay or overcharge in financial calculations.

## False-Positive Cautions

- No issue if the second adjustment is guarded by a distinct unit conversion that does not change value.
- Pure presentation rounding is lower risk without settlement use.
