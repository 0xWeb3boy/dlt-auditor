# Root-Cause Card

## Metadata

- ID: `reth-2025-04-19-reth-core-logic-6ef19f403`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-upper-bound-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch adds an explicit maximum-gas-limit check to `validate_header_gas` and introduces named consensus errors for over-maximum gas limits. The evidence supports a missing upper-bound check in a consensus-related validation function, but it does not prove a concrete vulnerability or that invalid blocks were previously accepted end-to-end.
