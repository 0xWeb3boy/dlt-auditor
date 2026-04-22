# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-10-28-oasis-core-staking-a34ab1924`
- Bug family: `staking_registry_and_accountability`
- Bug class: `slashability-bypass`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `lifecycle-accountability`

## Violated Invariant

- Invariant: Nodes that remain punishable during the staking debonding interval must remain internally resolvable, and an entity must not be removable while its registered nodes still exist.

## Trust Boundary

- Boundary: `client->query-verifier`

## Attack Surface

- Entrypoint type: `query-verification-path`
- Sensitive sink: `validator penalty state`

## Impact Pattern

- Primary impact: `slashing-bypass`
- Secondary impact: `accountability-loss`

## Short Reusable Lesson

- Nodes that remain punishable during the staking debonding interval must remain internally resolvable, and an entity must not be removable while its registered nodes still exist. In this pattern, registry cleanup and deregistration rules were too aggressive: node records could be removed on expiration before the staking debonding window ended, and entity removal did not enforce the continued existence of dependent node records. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
