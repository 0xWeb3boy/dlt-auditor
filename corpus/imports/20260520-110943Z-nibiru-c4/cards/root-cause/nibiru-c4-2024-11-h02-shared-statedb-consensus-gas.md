# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-h02-shared-statedb-consensus-gas`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `shared-statedb-query-state-leakage`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `query-state isolation`

## Violated Invariant

- Invariant: Read-only RPC simulations must not mutate keeper fields that influence later consensus transaction execution or gas accounting.

## Trust Boundary

- Boundary: rpc-client->node-local keeper state used by consensus execution

## Attack Surface

- Entrypoint type: eth_estimateGas or read-only EVM simulation
- Sensitive sink: bank keeper StateDB pointer and gas-affecting SyncStateDBWithAccount control flow

## Impact Pattern

- Primary impact: consensus gas nondeterminism
- Secondary impact: node-local RPC traffic influencing consensus execution

## Short Reusable Lesson

- NewStateDB assigned a pointer into a keeper field shared across read-only and state-mutating flows, and later bank methods branched on whether that field was nil.
