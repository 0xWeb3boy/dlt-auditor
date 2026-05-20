# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-i8-subtract-negative-branch-33175`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-i8-subtraction-branch-error`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the implementation delegates to a shared tested signed subtraction primitive.
- A single-width bug has lower scope if larger signed types are not affected.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Incorrect signed integer results can break financial calculations or freeze flows that rely on exact arithmetic.

## False-Positive Cautions

- No issue if the implementation delegates to a shared tested signed subtraction primitive.
- A single-width bug has lower scope if larger signed types are not affected.
