# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-yield-precompile-zero-required-gas`
- Bug family: `resource_accounting_and_limits`
- Bug class: `native-precompile-requiredgas-predicate`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `native-work-metering`

## Violated Invariant

- Invariant: Every valid native precompile selector should charge its intended RequiredGas before executing native state reads, writes, and share accounting.

## Trust Boundary

- Boundary: EVM call -> native precompile execution

## Attack Surface

- Entrypoint type: CALL/STATICCALL to Blast yield precompile
- Sensitive sink: StateDB yield accounting and Shares predeploy storage

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: fee-bypass

## Short Reusable Lesson

- Every valid native precompile selector should charge its intended RequiredGas before executing native state reads, writes, and share accounting. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
