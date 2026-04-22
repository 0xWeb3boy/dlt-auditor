# Root-Cause Card

## Metadata

- ID: `oasis-core-2020-04-22-oasis-core-staking-d477a90f7`
- Bug family: `staking_registry_and_accountability`
- Bug class: `incorrect-validator-voting-power`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `stake-to-power-consistency`

## Violated Invariant

- Invariant: In stake-based deployments, the validator set constructed by the scheduler should carry voting power derived from escrowed stake through a deterministic conversion. Flat voting power is only consistent with an explicit no-stake mode.

## Trust Boundary

- Boundary: `validator->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `validator voting power table`

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- In stake-based deployments, the validator set constructed by the scheduler should carry voting power derived from escrowed stake through a deterministic conversion. Flat voting power is only consistent with an explicit no-stake mode. In this pattern, the scheduler election path previously did not assign explicit stake-derived voting power in the shown validator-set construction path; the patch adds that missing mapping. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
