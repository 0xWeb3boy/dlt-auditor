# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ufp-exp-returns-one-33170`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-exp-result-discarded`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if exp is unused or explicitly documented as a stub.
- No issue if input is always zero and e^0 = 1 is expected.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Returning one for every exponent can break reward, interest, or pricing logic, but impact depends on adoption.

## False-Positive Cautions

- No issue if exp is unused or explicitly documented as a stub.
- No issue if input is always zero and e^0 = 1 is expected.
