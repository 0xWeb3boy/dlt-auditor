# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-zero-sign-change-33303`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `noncanonical-zero-sign`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if zero sign is never observable and all comparisons canonicalize.
- No issue if the library intentionally supports signed zero with documented semantics.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Noncanonical zero can break equality, comparison, or branch logic, with financial impact depending on use.

## False-Positive Cautions

- No issue if zero sign is never observable and all comparisons canonicalize.
- No issue if the library intentionally supports signed zero with documented semantics.
