# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-negative-other-33039`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-wrong-sign`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signed-operand-normalization`

## Violated Invariant

- Subtracting a negative operand must increase the result by that operand's magnitude, not subtract its biased encoding.

## Trust Boundary

- Boundary: `contract-input->integer-library`
- Entrypoint type: `library-function`
- Sensitive sink: `signed subtraction result used in balances or transfer amounts`

## Attack Surface

- Choose a negative other operand in signed integer subtraction.
- Trigger business logic that trusts signed library arithmetic.

## Exploit Preconditions

- The implementation adds or subtracts the biased underlying value without converting to magnitude.
- The resulting amount controls a transfer, debt, or reward calculation.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Library arithmetic must encode mathematical sign rules explicitly instead of relying on raw representation arithmetic.
