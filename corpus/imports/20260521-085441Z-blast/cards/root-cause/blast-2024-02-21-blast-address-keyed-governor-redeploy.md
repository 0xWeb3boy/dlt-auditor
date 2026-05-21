# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-address-keyed-governor-redeploy`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `durable-address-keyed-configuration`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `code-identity-binding`

## Violated Invariant

- Invariant: Gas/yield governor state that grants rights over a contract should be bound to the intended code identity or cleared/rebound across destructive lifecycle and redeploy events.

## Trust Boundary

- Boundary: contract address lifecycle -> Blast gas/yield governance

## Attack Surface

- Entrypoint type: CREATE2/metamorphic deployment or proxy/redeploy lifecycle
- Sensitive sink: Blast.governorMap and Gas per-address configuration

## Impact Pattern

- Primary impact: unauthorized-action
- Secondary impact: fee-claim-theft

## Short Reusable Lesson

- Gas/yield governor state that grants rights over a contract should be bound to the intended code identity or cleared/rebound across destructive lifecycle and redeploy events. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
