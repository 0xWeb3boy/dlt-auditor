# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-invalid-yield-precompile-zero-gas`
- Bug family: `resource_accounting_and_limits`
- Bug class: `invalid-precompile-revert-undercharge`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `native-error-path-metering`

## Violated Invariant

- Invariant: Malformed or unknown native precompile calls should still charge enough gas for native dispatch, parsing, rollback, and attribution work.

## Trust Boundary

- Boundary: EVM call -> native precompile error handling

## Attack Surface

- Entrypoint type: CALL/STATICCALL to Blast yield precompile with invalid calldata
- Sensitive sink: RunPrecompiledContract revert path and GasTracker attribution

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-accounting

## Short Reusable Lesson

- Malformed or unknown native precompile calls should still charge enough gas for native dispatch, parsing, rollback, and attribution work. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
