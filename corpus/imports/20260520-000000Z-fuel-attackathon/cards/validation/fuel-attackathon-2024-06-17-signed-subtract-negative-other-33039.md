# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-negative-other-33039`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-wrong-sign`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if callers never use negative operands.
- A wrong return value is lower risk without financial or authorization use.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Incorrect signed subtraction can produce wrong payment or accounting amounts in contracts using the library.

## False-Positive Cautions

- No issue if callers never use negative operands.
- A wrong return value is lower risk without financial or authorization use.
