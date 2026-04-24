# Root-Cause Card

## Metadata

- ID: `geth-arb-2021-07-22-go-ethereum-transaction-processing-97aacd9b35`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-balance-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `fee-and-value-balance-precheck`

## Violated Invariant

- Invariant: Transaction admission must check that the sender can cover both fee liability and transferred value under the active transaction type rules before state mutation.

## Trust Boundary

- Boundary: external transaction -> gas purchase and state transition

## Attack Surface

- Entrypoint type: transaction execution precheck
- Sensitive sink: gas purchase, balance debit, and value transfer

## Impact Pattern

- Primary impact: economic-integrity
- Secondary impact: state-integrity
- Severity guide: high

## Short Reusable Lesson

- The EIP-1559 balance precheck considered fee exposure but omitted transferred value, so affordability validation was incomplete before execution. Include transferred value in the transaction-type-specific balance check before buying gas or entering execution.
