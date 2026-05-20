# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ccp-zero-fill-undercharged-32465`
- Bug family: `resource_accounting_and_limits`
- Bug class: `undercharged-memory-zero-fill`
- Security verdict: `confirmed`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if the charged cost scales with the destination length including zero fill.
- Small bounded copies with equal charge and write length are not this pattern.

## Severity Guidance

- Expected impact band: `high`
- Expected severity band: `high`
- Rationale: A user can perform large memory writes for much less gas than equivalent memory-clear operations.

## False-Positive Cautions

- No issue if the charged cost scales with the destination length including zero fill.
- Small bounded copies with equal charge and write length are not this pattern.
