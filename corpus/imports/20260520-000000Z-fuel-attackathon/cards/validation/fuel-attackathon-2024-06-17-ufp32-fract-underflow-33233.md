# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ufp32-fract-underflow-33233`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-fraction-underflow`
- Security verdict: `confirmed`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the helper uses bit masks or modulo without underflow.
- No issue if all callers catch the revert and preserve liveness.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Every call to the helper can revert, making dependent contract functions unusable.

## False-Positive Cautions

- No issue if the helper uses bit masks or modulo without underflow.
- No issue if all callers catch the revert and preserve liveness.
