# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-maker-dsr-shutdown-strands-dai`
- Bug family: `staking_registry_and_accountability`
- Bug class: `external-provider-shutdown-recovery-gap`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `emergency-recovery-path`

## Violated Invariant

- Invariant: External staking-provider integration must support the provider shutdown/recovery mechanism for assets whose normal manager wrapper can no longer exit.

## Trust Boundary

- Boundary: Maker emergency shutdown -> Blast USD yield accounting

## Attack Surface

- Entrypoint type: DSRYieldProvider unstake or premium path after Maker cage/shutdown
- Sensitive sink: DSR_MANAGER.exit and DAI recovery ownership

## Impact Pattern

- Primary impact: asset-stranding
- Secondary impact: liveness-failure

## Short Reusable Lesson

- External staking-provider integration must support the provider shutdown/recovery mechanism for assets whose normal manager wrapper can no longer exit. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
