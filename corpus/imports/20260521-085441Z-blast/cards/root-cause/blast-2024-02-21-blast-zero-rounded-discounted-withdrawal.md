# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-zero-rounded-discounted-withdrawal`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `zero-rounded-positive-value-lifecycle`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `zero-progress-handling`

## Violated Invariant

- Invariant: A positive nominal withdrawal whose discounted value rounds to zero should be rejected before consuming state or recorded as replayable failure.

## Trust Boundary

- Boundary: discounted yield withdrawal -> cross-domain messenger replay state

## Attack Surface

- Entrypoint type: positive-value L2-to-L1 withdrawal during negative yield
- Sensitive sink: portal finalizedWithdrawals and messenger failedMessages/discountedValues

## Impact Pattern

- Primary impact: asset-stranding
- Secondary impact: cross-domain-lifecycle-failure

## Short Reusable Lesson

- A positive nominal withdrawal whose discounted value rounds to zero should be rejected before consuming state or recorded as replayable failure. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
