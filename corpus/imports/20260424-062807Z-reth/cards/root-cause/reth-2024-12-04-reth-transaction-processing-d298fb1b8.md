# Root-Cause Card

## Metadata

- ID: `reth-2024-12-04-reth-transaction-processing-d298fb1b8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: Optimism header admission must enforce fork-specific EIP-1559/base-fee rules in the consensus path. When Holocene is active according to the parent header timestamp, validation must use the Holocene rule that depends on parent-header data, and headers missing the required base-fee field must be rejected.

## Trust Boundary

- Boundary: transaction execution/precompile call -> gas accounting state

## Attack Surface

- Entrypoint type: state-transition/precompile-execution
- Sensitive sink: gas reservoir, receipt, and execution accounting

## Impact Pattern

- Primary impact: invalid-block-acceptance
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- Optimism header admission must enforce fork-specific EIP-1559/base-fee rules in the consensus path. When Holocene is active according to the parent header timestamp, validation must use the Holocene rule that depends on parent-header data, and headers missing the required base-fee field must be rejected.
