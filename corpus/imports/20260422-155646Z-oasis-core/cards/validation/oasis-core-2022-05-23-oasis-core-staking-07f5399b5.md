# Validation Card

## Metadata

- ID: `oasis-core-2022-05-23-oasis-core-staking-07f5399b5`
- Bug family: `staking_registry_and_accountability`
- Bug class: `reserved-address-invariant-enforcement`

## What Confirmed The Issue

- Evidence 1: The patch rerouted transfer-to-burn-address operations into shared burn logic via 'burnImpl(...)' and added sanity-check validation that rejects any burn-address ledger entry with non-zero balance or nonce.
- Evidence 2: The source finding states the invariant explicitly: 'staking.BurnAddress' must be treated as a burn sink, not as a normal transfer recipient, and ledger/genesis validation must reject non-zero balance or nonce for that address.

## What Could Have Invalidated It

- Compensating control 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Compensating control 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Caution 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.
