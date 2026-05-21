# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-reverted-tx-gas-allocation-profit`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `non-rollbacked-sidecar-accounting`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `sidecar-rollback-atomicity`

## Violated Invariant

- Invariant: Per-frame gas attribution sidecars should follow EVM rollback semantics when the attributed contract state and call frame revert.

## Trust Boundary

- Boundary: EVM execution/revert -> post-transaction gas finalizer

## Attack Surface

- Entrypoint type: reverting claimable-gas contract frame or failed transaction
- Sensitive sink: GasTracker.AllocateDevGas persistent claimable balance

## Impact Pattern

- Primary impact: fee-bypass
- Secondary impact: unauthorized-value-shift

## Short Reusable Lesson

- Per-frame gas attribution sidecars should follow EVM rollback semantics when the attributed contract state and call frame revert. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
