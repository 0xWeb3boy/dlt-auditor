# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-h01-vesting-account-preemption`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `account-type-preemption`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `address-space account-type isolation`

## Violated Invariant

- Invariant: A user-controllable Cosmos account type must not be able to reserve or poison a deterministic EVM contract address before code deployment.

## Trust Boundary

- Boundary: attacker-controlled vesting transaction->shared Cosmos/EVM address space

## Attack Surface

- Entrypoint type: vesting account creation transaction
- Sensitive sink: EVM contract account creation, code hash binding, and funds sent to a future contract address

## Impact Pattern

- Primary impact: deterministic contract address preemption
- Secondary impact: orphaned bytecode and locked deployment funds

## Short Reusable Lesson

- Vesting account creation accepted any target address in the shared account namespace, while EVM contract deployment only set code hashes for EthAccount-compatible accounts.
