# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-signed-subtract-biased-offset-33195`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `biased-signed-subtraction-formula-violation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `representation-invariant-enforcement`

## Violated Invariant

- For biased signed integers, subtraction must be equivalent to a_underlying - b_underlying + indent for every width.

## Trust Boundary

- Boundary: `contract-input->integer-library`
- Entrypoint type: `library-function`
- Sensitive sink: `signed subtraction result across all signed integer widths`

## Attack Surface

- Provide operands that enter each signed subtraction branch.
- Use the result in balances, rewards, debt, or control flow.

## Exploit Preconditions

- Multiple branches deviate from the canonical biased subtraction formula.
- The contract assumes library arithmetic is exact.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `high`

## Short Reusable Lesson

- For custom numeric encodings, derive operators from one invariant and test every branch against that invariant.
