# Root-Cause Card

## Metadata

- ID: `reth-2023-12-23-reth-transaction-processing-8fb6ed9cc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-fork-gating`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `fork-state-consistency`

## Violated Invariant

- Invariant: A typed transaction should only be accepted once the hardfork that enables that transaction type is active at the block being validated.

## Trust Boundary

- Boundary: block or transaction input -> execution-layer validator

## Attack Surface

- Entrypoint type: transaction/block-validation-path
- Sensitive sink: transaction acceptance or consensus rule application

## Impact Pattern

- Primary impact: improper-transaction-validation
- Secondary impact: none proven

## Short Reusable Lesson

- A typed transaction should only be accepted once the hardfork that enables that transaction type is active at the block being validated.
