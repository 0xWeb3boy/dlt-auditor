# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-h03-cross-runtime-staking-mint`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `cross-runtime-balance-desynchronization`

## Code Shape Summary

- Only some bank keeper wrappers synchronized EVM StateDB; staking, multisend, delegate, and undelegate paths could mutate balances without refreshing mirrored EVM state.

## Search Motifs

- SyncStateDBWithAccount missing wrapper
- DelegateCoinsFromAccountToModule
- Wasm staking capability called from EVM precompile
- SetAccBalance stale BalanceWei

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Add missing bank keeper method overrides or a central balance-change hook that synchronizes StateDB for every EVM-denom balance mutation.

## False Match Warnings

- No issue for denoms not mirrored into EVM StateDB.
- No issue if setBalance centrally synchronizes every balance-changing path.
- Need an EVM-visible stale balance to be committed after the native mutation.
