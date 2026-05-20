# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-zero-sign-change-33303`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `noncanonical-zero-sign`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-zero-normalization`

## Violated Invariant

- Adding equal magnitudes with opposite signs must produce canonical positive zero.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `signed fixed-point zero used by comparisons or later arithmetic`

## Attack Surface

- Add equal positive and negative values.
- Use the zero result in sign-sensitive logic.

## Exploit Preconditions

- The branch uses strict greater-than instead of greater-than-or-equal around equal magnitudes.
- Negative zero is observable in comparisons or downstream operations.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `contract-behavior-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Numeric types with separate sign metadata need explicit zero normalization after operations that cancel out.
