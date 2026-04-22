# Validation Card

## Metadata

- ID: `oasis-core-2020-04-22-oasis-core-staking-d477a90f7`
- Bug family: `staking_registry_and_accountability`
- Bug class: `incorrect-validator-voting-power`

## What Confirmed The Issue

- Evidence 1: The fix updates validator election to compute and store per-validator voting power instead of only collecting validator identities. It also introduces a shared scheduler API helper for converting escrowed stake into voting power and initializes the default conversion ratio used by that helper.
- Evidence 2: The source finding states the invariant explicitly: In stake-based deployments, the validator set constructed by the scheduler should carry voting power derived from escrowed stake through a deterministic conversion. Flat voting power is only consistent with an explicit no-stake mode.

## What Could Have Invalidated It

- Compensating control 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Compensating control 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Caution 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.
