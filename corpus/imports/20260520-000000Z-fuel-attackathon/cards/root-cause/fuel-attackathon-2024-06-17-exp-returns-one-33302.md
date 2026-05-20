# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-exp-returns-one-33302`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-exp-result-discarded`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `computed-result-binding`

## Violated Invariant

- Fixed-point exp must return a value derived from its input for non-zero exponents.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `exponential math output used by dependent contracts`

## Attack Surface

- Call exp with non-zero input.
- Rely on the result for financial calculations.

## Exploit Preconditions

- The function returns the one constant instead of one plus the computed series.
- A contract uses exp for settlement-sensitive formulas.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Tests for math helpers should assert output changes with input, catching accidentally constant returns.
