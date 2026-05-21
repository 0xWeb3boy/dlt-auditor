# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-upgrade-reinitializer-double-withdrawal`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `upgrade-reinitializer-reentrancy-reset`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `active-replay-guard-preservation`

## Violated Invariant

- Invariant: Upgrade initializers must not reset active reentrancy/replay guard state while a failed value-bearing message retry is executing.

## Trust Boundary

- Boundary: governance upgrade transaction -> active cross-domain message relay

## Attack Surface

- Entrypoint type: failed value-bearing relay target that executes signed upgrade and reenters relayMessage
- Sensitive sink: xDomainMsgSender guard and successfulMessages/failedMessages maps

## Impact Pattern

- Primary impact: double-withdrawal
- Secondary impact: asset-drain

## Short Reusable Lesson

- Upgrade initializers must not reset active reentrancy/replay guard state while a failed value-bearing message retry is executing. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
