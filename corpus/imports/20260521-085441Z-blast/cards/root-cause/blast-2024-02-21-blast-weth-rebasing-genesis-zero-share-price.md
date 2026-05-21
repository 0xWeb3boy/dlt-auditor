# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-weth-rebasing-genesis-zero-share-price`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `initializer-genesis-state-mismatch`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `initializer-postcondition-parity`

## Violated Invariant

- Invariant: Genesis storage for initialized proxied predeploys must include all storage postconditions of the initializer, especially accounting price and share state.

## Trust Boundary

- Boundary: genesis builder -> live L2 predeploy state

## Attack Surface

- Entrypoint type: L2 genesis construction
- Sensitive sink: WETHRebasing ERC20 share-price and total-share accounting

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: asset-yield-loss

## Short Reusable Lesson

- Genesis storage for initialized proxied predeploys must include all storage postconditions of the initializer, especially accounting price and share state. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
