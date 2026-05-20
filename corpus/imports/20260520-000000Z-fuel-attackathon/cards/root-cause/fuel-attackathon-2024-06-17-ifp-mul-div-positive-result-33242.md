# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-positive-result-33242`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `operand-sign-comparison`

## Violated Invariant

- Signed fixed-point multiplication and division must return a negative result exactly when one operand is negative.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `signed fixed-point result used in contract accounting`

## Attack Surface

- Choose mixed-sign operands.
- Reach IFP multiply or divide in settlement, reward, or debt logic.

## Exploit Preconditions

- The sign calculation compares an operand to itself instead of the other operand.
- The erroneous positive result is trusted.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Numeric library operators should be tested over a complete sign matrix, not just magnitude examples.
