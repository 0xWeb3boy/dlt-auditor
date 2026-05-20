# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-ceil-negative-sign-32696`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-rounding-sign-misbinding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `sign-propagation-invariant`

## Violated Invariant

- Fixed-point rounding must return the mathematically correct sign for the rounded value, including transitions around zero.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `rounded fixed-point amount used by downstream contracts`

## Attack Surface

- Supply negative fixed-point values near a rounding boundary.
- Trigger contract logic that relies on ceil or round.

## Exploit Preconditions

- ceil computes a positive rounded underlying value but returns the original negative sign flag.
- Downstream code trusts the sign flag for value transfers or accounting.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Composite numeric types must update metadata such as sign flags whenever arithmetic changes the represented value.
