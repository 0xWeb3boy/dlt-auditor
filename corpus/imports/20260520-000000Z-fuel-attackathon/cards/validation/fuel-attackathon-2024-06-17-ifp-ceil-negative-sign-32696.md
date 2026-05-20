# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-ceil-negative-sign-32696`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-rounding-sign-misbinding`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if callers ignore the sign flag and use a canonical numeric representation.
- A display-only rounding bug has lower severity without asset accounting use.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Wrong sign on rounded fixed-point values can invert financial accounting in contracts using the library.

## False-Positive Cautions

- No issue if callers ignore the sign flag and use a canonical numeric representation.
- A display-only rounding bug has lower severity without asset accounting use.
