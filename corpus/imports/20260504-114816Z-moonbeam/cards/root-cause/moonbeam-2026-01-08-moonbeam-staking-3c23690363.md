# Root-Cause Card

## Metadata

- ID: `moonbeam-2026-01-08-moonbeam-staking-3c23690363`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-corruption`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `cumulative-pending-delegation-accounting`

## Violated Invariant

- Invariant: Pending balance-changing requests must be validated and aggregated cumulatively before they affect stake snapshots or reward denominators.

## Trust Boundary

- Boundary: Delegator-scheduled requests cross from a queue into monetary reward accounting.

## Attack Surface

- Entrypoint type: staking-delegation-decrease-request
- Sensitive sink: reward snapshot uncounted_stake and payout denominator

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: economic-accounting, reward-overmint-or-misallocation

## Short Reusable Lesson

- Validation checked a new decrease in isolation while reward snapshot code aggregated all pending decreases. The fix sums pending decreases during validation and caps accounting by actual bonded amount. Apply cumulative pending-request validation and cap derived reward accounting at the actual bonded balance before payout math.
