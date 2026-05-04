# Root-Cause Card

## Metadata

- ID: `moonbeam-2026-01-08-moonbeam-staking-5f3e4b30c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-corruption`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `cumulative-pending-delegation-accounting`

## Violated Invariant

- Invariant: A queue of pending stake decreases must never reduce counted stake by more than the real bonded amount for that delegation.

## Trust Boundary

- Boundary: User-scheduled staking operations cross into reward snapshot construction.

## Attack Surface

- Entrypoint type: staking-delegation-decrease-request
- Sensitive sink: reward snapshot denominator and payout allocation

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: economic-accounting, reward-overmint-or-misallocation

## Short Reusable Lesson

- Request acceptance and reward accounting used inconsistent views of pending decreases. The patch aggregates scheduled decreases and clamps accounting to the real bond. Use one cumulative invariant for pending stake decreases across request admission and reward snapshot aggregation.
