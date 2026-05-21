# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-discounted-messenger-reserved-gas`
- Bug family: `resource_accounting_and_limits`
- Bug class: `bridge-failure-record-gas-underreserve`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `failure-state-gas-reservation`

## Violated Invariant

- Invariant: Portal finalization must not become permanent unless messenger success or replayable failure state, including discounted value sidecars, can be durably recorded within the reserved gas.

## Trust Boundary

- Boundary: L2-to-L1 message finalization -> L1 messenger failure state

## Attack Surface

- Entrypoint type: OptimismPortal.finalizeWithdrawalTransaction targeting L1CrossDomainMessenger
- Sensitive sink: failedMessages and discountedValues storage writes

## Impact Pattern

- Primary impact: asset-stranding
- Secondary impact: cross-domain-lifecycle-failure

## Short Reusable Lesson

- Portal finalization must not become permanent unless messenger success or replayable failure state, including discounted value sidecars, can be durably recorded within the reserved gas. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
