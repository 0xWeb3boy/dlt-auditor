# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-underflow-branch-32706`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-underflow`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `biased-arithmetic-branch-coverage`

## Violated Invariant

- Signed subtraction over a biased unsigned representation must handle every sign combination without underflow or sign inversion.

## Trust Boundary

- Boundary: `contract-input->integer-library`
- Entrypoint type: `library-function`
- Sensitive sink: `signed subtraction result used by contract accounting`

## Attack Surface

- Provide operands on opposite sides of the signed indent value.
- Reach subtraction in contract math with attacker-influenced values.

## Exploit Preconditions

- The branch for self below indent and other above indent subtracts a larger value from a smaller one.
- VM arithmetic panics or returns an invalid value instead of the signed result.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `denial-of-service`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Signed arithmetic implemented over biased unsigned storage needs exhaustive branch tests over every sign quadrant.
