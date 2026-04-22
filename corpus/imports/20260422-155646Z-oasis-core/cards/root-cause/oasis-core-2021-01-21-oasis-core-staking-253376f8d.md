# Root-Cause Card

## Metadata

- ID: `oasis-core-2021-01-21-oasis-core-staking-253376f8d`
- Bug family: `staking_registry_and_accountability`
- Bug class: `insufficient-validator-slashing-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `slashing-enforcement`

## Violated Invariant

- Invariant: Runtime misbehavior penalties should be representable in the runtime staking parameters and processed without failing on expected edge cases such as stale evidence or zero available funds.

## Trust Boundary

- Boundary: `validator->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `validator penalty state`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- Runtime misbehavior penalties should be representable in the runtime staking parameters and processed without failing on expected edge cases such as stale evidence or zero available funds. In this pattern, the evidence supports an incomplete or brittle slashing/accounting implementation: policy fields and parsing were missing from the shown registration/API paths, and the slashing/fund-transfer code handled zero-funds cases harshly. The evidence does not prove a stronger root cause such as successful acceptance of incorrect results. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
