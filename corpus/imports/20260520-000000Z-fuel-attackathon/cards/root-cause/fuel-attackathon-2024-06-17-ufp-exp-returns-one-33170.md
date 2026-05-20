# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-ufp-exp-returns-one-33170`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `fixed-point-exp-result-discarded`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `computed-result-binding`

## Violated Invariant

- A math helper must return the computed approximation, not a constant placeholder.

## Trust Boundary

- Boundary: `contract-input->financial-math-library`
- Entrypoint type: `library-function`
- Sensitive sink: `exp result used in interest, rewards, pricing, or decay`

## Attack Surface

- Call exp with any non-zero input.
- Use the result in financial formulas.

## Exploit Preconditions

- The implementation computes res_minus_1 but returns one.
- The protocol relies on exponential growth or decay.

## Impact Pattern

- Primary impact: `arithmetic-integrity`
- Secondary impact: `asset-integrity`
- Blast radius: `ecosystem-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Math-library tests need non-trivial vectors that prove computed intermediates affect the returned value.
