# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-h05-precompile-statedb-commit-clobber`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `precompile-statedb-commit-clobber`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `single authoritative EVM state view`

## Violated Invariant

- Invariant: Nested EVM calls from precompiles must commit through the same authoritative StateDB view as the outer EthereumTx, including dirty storage and balance changes.

## Trust Boundary

- Boundary: EVM contract->FunToken precompile->nested EVM CallContract

## Attack Surface

- Entrypoint type: precompile nested contract call
- Sensitive sink: StateDB commit of ERC20 balances and contract storage after FunToken conversion

## Impact Pattern

- Primary impact: ERC20/bank double-spend through stale StateDB commit
- Secondary impact: contract storage corruption risk

## Short Reusable Lesson

- FunToken precompile nested calls updated a cache context while outer EthereumTx committed stale or dirtied StateDB objects back over those changes.
