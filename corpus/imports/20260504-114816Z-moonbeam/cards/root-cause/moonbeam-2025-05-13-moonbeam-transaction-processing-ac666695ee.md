# Root-Cause Card

## Metadata

- ID: `moonbeam-2025-05-13-moonbeam-transaction-processing-ac666695ee`
- Bug family: `resource_accounting_and_limits`
- Bug class: `evm-resource-accounting-and-reentrancy-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `canonical-resource-accounting-representation`

## Violated Invariant

- Invariant: Runtime API paths that simulate or trace EVM calls must use the same canonical transaction data model and reentrancy policy as normal execution.

## Trust Boundary

- Boundary: RPC/runtime API callers cross into EVM execution simulation and resource estimation logic.

## Attack Surface

- Entrypoint type: evm-runtime-api-call-tracing
- Sensitive sink: proof-size/base-cost and reentrancy policy for EVM runtime APIs

## Impact Pattern

- Primary impact: resource-accounting
- Secondary impact: denial-of-service, reentrancy-hardening

## Short Reusable Lesson

- Runtime API paths hand-rolled transaction length/proof-size estimates. The patch constructs pallet_ethereum::TransactionData and enables forbid-evm-reentrancy. Replace duplicated local size accounting with canonical pallet transaction data and enable the pallet-provided reentrancy guard feature.
