# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-sway-libs-arithmetic-correctness-bundle-32275`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `numeric-library-invariant-bundle`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- A precision tradeoff is lower risk if documented and not used for settlement.
- A library bug is less severe when no reachable contract path uses the affected helper.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: The report groups many correctness defects; individual exploitability depends on which helper a contract uses.

## False-Positive Cautions

- A precision tradeoff is lower risk if documented and not used for settlement.
- A library bug is less severe when no reachable contract path uses the affected helper.
