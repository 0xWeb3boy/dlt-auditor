# Validation Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-impl-dependency-name-collision-32973`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `compiler-symbol-identity-collision`
- Security verdict: `likely`
- Validated as: `public-attackathon-finding`

## What Confirmed The Issue

- Public attackathon report includes a concrete vulnerable code path and proof-of-concept or reproduction notes.
- The vulnerable shape violates the reusable invariant recorded for this corpus entry.

## What Could Have Invalidated It

- No issue if impl blocks receive unique node ids independent of declaration names.
- A collision that always hard-fails compilation has liveness impact but less security risk.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Most collisions may fail compilation, but surviving type confusion can alter ABI encoding or contract behavior.

## False-Positive Cautions

- No issue if impl blocks receive unique node ids independent of declaration names.
- A collision that always hard-fails compilation has liveness impact but less security risk.
