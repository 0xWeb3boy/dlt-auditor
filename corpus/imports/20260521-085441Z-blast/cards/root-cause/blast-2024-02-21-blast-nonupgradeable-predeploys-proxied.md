# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-nonupgradeable-predeploys-proxied`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `constructor-only-contract-behind-proxy`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `proxy-intent-and-initializer-model`

## Violated Invariant

- Invariant: Contracts intended to rely on constructor-only invariants should either not be proxied or should provide initializer/reinitializer paths and tests for every proxy upgrade scenario.

## Trust Boundary

- Boundary: genesis/deployment proxy admin -> system predeploy logic

## Attack Surface

- Entrypoint type: L2 predeploy proxy installation and future ProxyAdmin upgrade
- Sensitive sink: Blast and Gas predeploy implementation and mutable configuration

## Impact Pattern

- Primary impact: upgrade-safety
- Secondary impact: unauthorized-action

## Short Reusable Lesson

- Contracts intended to rely on constructor-only invariants should either not be proxied or should provide initializer/reinitializer paths and tests for every proxy upgrade scenario. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
