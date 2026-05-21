# Root-Cause Card

## Metadata

- ID: `blast-2024-02-21-blast-insurance-fresh-steth-front-run`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `loss-eligibility-snapshot-gap`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `loss-time-eligibility-binding`

## Violated Invariant

- Invariant: Insurance or recovery for an externally known provider loss should apply to holders exposed at loss time, not fresh entrants who deposit after observing the loss.

## Trust Boundary

- Boundary: external provider impairment -> bridge deposit and insurance accounting

## Attack Surface

- Entrypoint type: fresh stETH deposit before loss report/insurance repair
- Sensitive sink: ETH yield manager share minting and insurance repair distribution

## Impact Pattern

- Primary impact: value-transfer-between-cohorts
- Secondary impact: insurance-drain

## Short Reusable Lesson

- Insurance or recovery for an externally known provider loss should apply to holders exposed at loss time, not fresh entrants who deposit after observing the loss. Bugs in this class often appear when rollup bridges, native precompiles, yield managers, or gas-accounting sidecars add protocol-specific state transitions without carrying the same invariant through every lifecycle branch, error branch, and upgrade path.
