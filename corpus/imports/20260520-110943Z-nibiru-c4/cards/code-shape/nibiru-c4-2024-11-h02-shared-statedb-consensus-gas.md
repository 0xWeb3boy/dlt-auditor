# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-h02-shared-statedb-consensus-gas`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `shared-statedb-query-state-leakage`

## Code Shape Summary

- NewStateDB assigned a pointer into a keeper field shared across read-only and state-mutating flows, and later bank methods branched on whether that field was nil.

## Search Motifs

- keeper field StateDB *statedb.StateDB
- NewStateDB assigns evmKeeper.Bank.StateDB
- eth_estimateGas mutates keeper pointer
- SyncStateDBWithAccount nil check affects gas

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Avoid multiple/shared StateDB copies during EVM execution and clear or scope the bank StateDB pointer so read-only calls cannot affect later consensus paths.

## False Match Warnings

- No issue if the pointer is scoped only to the current transaction context.
- No issue if read-only queries use isolated keeper copies.
- No issue if nil vs non-nil has no consensus-visible behavior or gas difference.
