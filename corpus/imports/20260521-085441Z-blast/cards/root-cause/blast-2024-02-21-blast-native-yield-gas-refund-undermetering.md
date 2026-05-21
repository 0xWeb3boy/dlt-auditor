# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-native-yield-gas-refund-undermetering`
- Bug family: `resource_accounting_and_limits`
- Bug class: `native-bookkeeping-undermetering`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `native-work-gas-budget`

## Violated Invariant

- Invariant: Gas costs for opcodes and transactions should cover the extra native bookkeeping added by yield and gas-refund features, including per-account and global predeploy storage effects.

## Trust Boundary

- Boundary: EVM transaction/opcode gas schedule -> Blast native StateDB side effects

## Attack Surface

- Entrypoint type: balance changes, selfdestruct, gas allocation finalization, claimable gas updates
- Sensitive sink: Shares and Gas predeploy storage plus StateDB journals

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-accounting

## Short Reusable Lesson

- Gas costs for opcodes and transactions should cover the extra native bookkeeping added by yield and gas-refund features, including per-account and global predeploy storage effects. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
