# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-small-type-alu-overflow-33331`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `narrow-integer-overflow-check-missing`
- Security verdict: `confirmed`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the operation is performed on true u64/u256 where VM overflow semantics match the type.
- No issue if the compiler inserts declared-width checks before return and storage.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: Stored values can exceed their source type and later wrap or misencode, corrupting contract or SDK accounting.

## False-Positive Cautions

- No issue if the operation is performed on true u64/u256 where VM overflow semantics match the type.
- No issue if the compiler inserts declared-width checks before return and storage.
