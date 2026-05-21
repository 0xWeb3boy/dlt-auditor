# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-uninitialized-usd-yield-manager-implementation`
- Bug family: `authz_and_role_gates`
- Bug class: `unlocked-proxy-implementation-initializer`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `implementation-initializer-locking`

## Violated Invariant

- Invariant: Implementation contracts behind proxies must not remain publicly initializable when initialization grants ownership or reaches delegatecall hooks.

## Trust Boundary

- Boundary: external caller -> implementation contract address

## Attack Surface

- Entrypoint type: direct initialize call on implementation
- Sensitive sink: owner-only provider registration and delegatecall to provider code

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: upgrade-safety

## Short Reusable Lesson

- Implementation contracts behind proxies must not remain publicly initializable when initialization grants ownership or reaches delegatecall hooks. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
