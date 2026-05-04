# Validation Card

## Metadata

- ID: `moonbeam-2026-01-08-moonbeam-staking-5f3e4b30c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-corruption`

## What Confirmed The Issue

- Validation now aggregates pending DelegationAction::Decrease amounts.
- Snapshot path uses min(amount, bond.amount) before rewardable stake math.

## What Could Have Invalidated It

- No path permits stacked decreases for the same collator/delegator pair
- A later settlement stage independently rejects over-decreased rewards before minting

## Severity Guidance

- Expected impact band: staking_economic_integrity
- Expected severity band: high

## False-Positive Cautions

- If request queue enforces one active decrease, cumulative validation is redundant
- If rewards are recomputed from actual balances only, denominator corruption may be non-security
