# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-negative-result-33267`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if using an unaffected version with sign-matrix tests.
- No issue if all values are unsigned by design.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Mixed-sign fixed-point operations return positive values, which can invert financial meaning.

## False-Positive Cautions

- No issue if using an unaffected version with sign-matrix tests.
- No issue if all values are unsigned by design.
