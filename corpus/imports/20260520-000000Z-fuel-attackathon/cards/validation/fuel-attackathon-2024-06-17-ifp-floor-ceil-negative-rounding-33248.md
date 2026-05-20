# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-floor-ceil-negative-rounding-33248`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-negative-rounding-error`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the helper is not used for settlement-sensitive values.
- No issue if negative values are disallowed at type boundaries.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Negative fixed-point rounding errors can overpay, underpay, or revert financial flows.

## False-Positive Cautions

- No issue if the helper is not used for settlement-sensitive values.
- No issue if negative values are disallowed at type boundaries.
