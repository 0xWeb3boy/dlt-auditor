# Root-Cause Card

## Metadata

- ID: `moonbeam-2021-02-12-moonbeam-storage-1490dbf7f6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `historical-reward-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `historical-state-snapshot-consistency`

## Violated Invariant

- Invariant: Delayed reward settlement must use the immutable stake exposure from the earning period, not mutable live stake state from payout time.

## Trust Boundary

- Boundary: Current staking state crosses into a historical accounting calculation that should be bound to a prior round snapshot.

## Attack Surface

- Entrypoint type: delayed-reward-settlement
- Sensitive sink: staking reward distribution denominator and payout allocation

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: economic-accounting, reward-misallocation

## Short Reusable Lesson

- A delayed payout function read live candidate/delegator state while settling rewards for an earlier round. The fix introduced/used round-indexed AtStake snapshots for payout weighting. Record immutable per-round exposure and consume that snapshot during delayed settlement instead of querying mutable candidate state.
