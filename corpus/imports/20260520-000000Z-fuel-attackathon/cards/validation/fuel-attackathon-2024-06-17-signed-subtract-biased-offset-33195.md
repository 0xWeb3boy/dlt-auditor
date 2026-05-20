# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-biased-offset-33195`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-formula-violation`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if exhaustive branch tests show equivalence to mathematical subtraction.
- Pure documentation mismatch is not enough without executable wrong results.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: A systematic signed arithmetic error across widths can propagate into many financial contracts.

## False-Positive Cautions

- No issue if exhaustive branch tests show equivalence to mathematical subtraction.
- Pure documentation mismatch is not enough without executable wrong results.
