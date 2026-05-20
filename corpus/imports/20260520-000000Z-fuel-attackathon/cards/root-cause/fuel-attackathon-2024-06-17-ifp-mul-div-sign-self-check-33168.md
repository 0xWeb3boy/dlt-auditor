# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ifp-mul-div-sign-self-check-33168`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-multiply-divide-sign-misbinding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `operand-sign-comparison`

## Violated Invariant

- Multiplication and division of signed fixed-point values must set the result sign from both operands.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `fixed-point multiply or divide result used by financial logic`

## Attack Surface

- Supply one negative and one positive operand.
- Trigger multiply or divide in a contract that relies on signed fixed-point math.

## Exploit Preconditions

- The sign expression compares self.non_negative with itself.
- Downstream financial logic treats the returned sign as authoritative.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Signed numeric library tests should cover the full operand sign matrix for every arithmetic operator.
