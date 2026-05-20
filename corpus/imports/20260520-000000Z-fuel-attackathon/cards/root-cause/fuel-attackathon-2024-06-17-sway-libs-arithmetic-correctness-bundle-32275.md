# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-sway-libs-arithmetic-correctness-bundle-32275`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `numeric-library-invariant-bundle`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `numeric-library-spec-conformance`

## Violated Invariant

- Core integer and fixed-point library helpers must preserve documented widths, signs, denominators, and precision across all edge cases.

## Trust Boundary

- Boundary: `contract-input->standard-library-math`
- Entrypoint type: `library-function`
- Sensitive sink: `multiple signed, unsigned, and fixed-point math helper results`

## Attack Surface

- Use edge-case numeric values around widths, signs, denominators, min/max, or zero.
- Reach any affected math helper in contract logic.

## Exploit Preconditions

- Library implementations duplicate numeric rules across widths without exhaustive invariant tests.
- Contracts trust library functions for asset or liveness decisions.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Security-sensitive math libraries need invariant-driven tests across widths, signs, precision, and boundary values.
