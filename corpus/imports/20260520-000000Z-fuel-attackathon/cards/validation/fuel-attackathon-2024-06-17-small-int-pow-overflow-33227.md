# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-small-int-pow-overflow-33227`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `small-width-pow-overflow`
- Security verdict: `confirmed`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the operation returns a Result or panics before exceeding the declared type max.
- u64 and u256 behavior may be covered by separate VM checks.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Overflowed narrow-type powers can produce wrong transfer amounts or wrap when crossing SDK boundaries.

## False-Positive Cautions

- No issue if the operation returns a Result or panics before exceeding the declared type max.
- u64 and u256 behavior may be covered by separate VM checks.
