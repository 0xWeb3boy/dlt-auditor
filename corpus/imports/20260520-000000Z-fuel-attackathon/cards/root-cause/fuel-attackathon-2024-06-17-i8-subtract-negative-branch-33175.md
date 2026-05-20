# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-i8-subtract-negative-branch-33175`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-i8-subtraction-branch-error`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signed-branch-correctness`

## Violated Invariant

- Subtracting two negative signed integers must preserve the biased offset and return the correct mathematical sign.

## Trust Boundary

- Boundary: `contract-input->integer-library`
- Entrypoint type: `library-function`
- Sensitive sink: `I8 subtraction result used by downstream contract logic`

## Attack Surface

- Choose negative I8 operands such as -2 and -3.
- Reach library subtraction in a contract flow.

## Exploit Preconditions

- The branch for one negative operand adds indent where it should subtract or normalize it.
- The wrong result feeds contract decisions.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Representative examples like -2 minus -3 catch branch errors that broad positive-only arithmetic tests miss.
