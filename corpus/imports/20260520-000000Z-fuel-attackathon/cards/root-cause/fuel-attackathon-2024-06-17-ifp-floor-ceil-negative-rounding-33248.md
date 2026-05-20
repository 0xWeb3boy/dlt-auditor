# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-floor-ceil-negative-rounding-33248`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-negative-rounding-error`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `negative-rounding-invariants`

## Violated Invariant

- floor and ceil for signed fixed-point values must obey mathematical rounding rules for negative inputs.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `rounded fixed-point values in contract logic`

## Attack Surface

- Supply negative fractional inputs.
- Trigger floor, ceil, or round in financial calculations.

## Exploit Preconditions

- The implementation uses the wrong unit conversion and subtracts even when already rounded.
- Contracts assume the library implements mathematical floor and ceil.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Rounding routines need explicit tests for negative exact values, negative fractional values, and zero crossings.
