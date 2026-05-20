# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-positive-result-33242`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the affected library version is not used.
- No issue if negative values are rejected before all IFP multiply/divide calls.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Every mixed-sign multiply/divide can be returned with the wrong sign in contracts that depend on the library.

## False-Positive Cautions

- No issue if the affected library version is not used.
- No issue if negative values are rejected before all IFP multiply/divide calls.
