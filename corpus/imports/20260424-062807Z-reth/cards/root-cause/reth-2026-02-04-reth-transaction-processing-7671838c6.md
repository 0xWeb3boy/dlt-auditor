# Root-Cause Card

## Metadata

- ID: `reth-2026-02-04-reth-transaction-processing-7671838c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-rule-enforcement`

## Violated Invariant

- Invariant: After EIP-7778/Amsterdam, block validation must keep two gas-accounting meanings separate: block-header gas_used must be checked against execution-result gas_used, while receipt cumulative_gas_used must remain the receipt-format value. Validation and receipt construction must not treat those values as interchangeable.

## Trust Boundary

- Boundary: transaction execution/precompile call -> gas accounting state

## Attack Surface

- Entrypoint type: state-transition/precompile-execution
- Sensitive sink: gas reservoir, receipt, and execution accounting

## Impact Pattern

- Primary impact: consensus-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- After EIP-7778/Amsterdam, block validation must keep two gas-accounting meanings separate: block-header gas_used must be checked against execution-result gas_used, while receipt cumulative_gas_used must remain the receipt-format value. Validation and receipt construction must not treat those values as interchangeable.
