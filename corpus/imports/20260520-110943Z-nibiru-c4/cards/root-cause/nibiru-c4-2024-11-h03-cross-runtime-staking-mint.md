# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-h03-cross-runtime-staking-mint`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `cross-runtime-balance-desynchronization`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `cross-runtime balance synchronization`

## Violated Invariant

- Invariant: Every native bank balance change for the EVM denom must refresh the mirrored EVM StateDB balance before EVM-visible state can be committed.

## Trust Boundary

- Boundary: EVM contract->Wasm staking capability->native bank keeper

## Attack Surface

- Entrypoint type: EVM precompile invoking Wasm staking operations
- Sensitive sink: bank setBalance for delegated coins and EVM StateDB SetAccBalance reconciliation

## Impact Pattern

- Primary impact: unbacked native token minting
- Secondary impact: cross-runtime accounting drift

## Short Reusable Lesson

- Only some bank keeper wrappers synchronized EVM StateDB; staking, multisend, delegate, and undelegate paths could mutate balances without refreshing mirrored EVM state.
