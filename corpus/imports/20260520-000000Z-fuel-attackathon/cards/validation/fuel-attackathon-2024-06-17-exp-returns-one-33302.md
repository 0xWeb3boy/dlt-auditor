# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-exp-returns-one-33302`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-exp-result-discarded`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue for e^0 only.
- No issue if the affected function is not exported or reachable in the used version.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Constant exp output can break any protocol relying on growth, decay, or compounding math.

## False-Positive Cautions

- No issue for e^0 only.
- No issue if the affected function is not exported or reachable in the used version.
