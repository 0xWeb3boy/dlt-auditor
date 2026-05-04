# Validation Card

## Metadata

- ID: `moonbeam-2026-01-08-moonbeam-staking-3c23690363`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-corruption`

## What Confirmed The Issue

- delegation_requests.rs computes total pending decrease amount.
- reward snapshot code caps pending decrease accounting by current bond amount and adds regression coverage.

## What Could Have Invalidated It

- Storage model prevents more than one pending decrease per pair
- Reward payout uses a separate invariant that ignores uncounted_stake for monetary distribution

## Severity Guidance

- Expected impact band: staking_economic_integrity
- Expected severity band: high

## False-Positive Cautions

- Single pending action per pair enforced by storage key uniqueness is safe
- Pending decreases not used in payout denominator are lower impact
