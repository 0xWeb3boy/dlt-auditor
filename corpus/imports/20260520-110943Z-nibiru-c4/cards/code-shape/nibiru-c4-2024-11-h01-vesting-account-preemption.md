# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-h01-vesting-account-preemption`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `account-type-preemption`

## Code Shape Summary

- Vesting account creation accepted any target address in the shared account namespace, while EVM contract deployment only set code hashes for EthAccount-compatible accounts.

## Search Motifs

- CreatePermanentLockedAccount target address
- vesting account at EVM contract address
- SetAccount only sets CodeHash for EthAccountI
- crypto.CreateAddress precomputed child address

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Disable built-in auth/vesting transaction messages or otherwise reject vesting account creation for addresses that can be valid EVM contract accounts.

## False Match Warnings

- No issue if vesting creation is governance-only or disabled.
- No issue if EVM contract accounts live in a disjoint address namespace.
- No issue if deployment converts or rejects pre-existing non-EVM accounts before storing code.
