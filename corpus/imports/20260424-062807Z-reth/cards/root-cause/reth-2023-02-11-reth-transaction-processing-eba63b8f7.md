# Root-Cause Card

## Metadata

- ID: `reth-2023-02-11-reth-transaction-processing-eba63b8f7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-transition-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: Paris activation at the terminal total difficulty boundary must be evaluated with both cumulative total difficulty and the current block or payload difficulty so pre-merge and post-merge rules are applied on the correct side of the transition.

## Trust Boundary

- Boundary: block or transaction input -> execution-layer validator

## Attack Surface

- Entrypoint type: transaction/block-validation-path
- Sensitive sink: transaction acceptance or consensus rule application

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- Paris activation at the terminal total difficulty boundary must be evaluated with both cumulative total difficulty and the current block or payload difficulty so pre-merge and post-merge rules are applied on the correct side of the transition.
