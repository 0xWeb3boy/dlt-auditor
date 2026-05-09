# Code-Shape Card

## Metadata

- ID: `nibiru-2025-01-26-nibiru-staking-3f5be387`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cross-runtime-state-sync`

## Code Shape Summary

- A native bank delegation wrapper now synchronizes EVM-visible account state for both sender and recipient module accounts after EVM-denom balance movement.

## Search Motifs

- DelegateCoinsFromAccountToModule wrapper
- SyncStateDBWithAccount after bank delegation
- DirtyStateAttack regression
- module account balance changes not mirrored to EVM StateDB

## Typical Asymmetry

- The trusted protocol side assumes a helper, callback, registry, iterator, or accounting result is already safe; the attacker controls the input, callee, ordering, or transaction shape that reaches that trusted sink.

## Patch Pattern

- Wrap native module transfers for mirrored denoms and refresh all affected runtime account caches immediately after the native operation succeeds.

## False Match Warnings

- Do not flag transfers of denoms not mirrored into the foreign runtime
- Need subsequent runtime visibility or cache dependence
- A sync on only sender may be insufficient when recipient is a module account
