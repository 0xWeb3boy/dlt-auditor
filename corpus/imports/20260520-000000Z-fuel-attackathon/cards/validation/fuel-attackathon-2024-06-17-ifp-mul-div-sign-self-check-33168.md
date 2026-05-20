# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-sign-self-check-33168`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue in unsigned fixed-point math.
- No issue if callers reject negative operands before reaching multiply or divide.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Negative products or quotients can be returned as positive values, corrupting debt, reward, or balance math.

## False-Positive Cautions

- No issue in unsigned fixed-point math.
- No issue if callers reject negative operands before reaching multiply or divide.
