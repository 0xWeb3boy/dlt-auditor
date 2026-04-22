# Validation Card

## Metadata

- ID: `oasis-core-2019-10-28-oasis-core-staking-a34ab1924`
- Bug family: `staking_registry_and_accountability`
- Bug class: `slashability-bypass`

## What Confirmed The Issue

- Evidence 1: The registry now keeps expired nodes for the staking debonding interval, prevents entity deregistration when the entity still has registered nodes, hides expired retained nodes from query results, and reuses existing node status when such a node is registered again.
- Evidence 2: The source finding states the invariant explicitly: Nodes that remain punishable during the staking debonding interval must remain internally resolvable, and an entity must not be removable while its registered nodes still exist.

## What Could Have Invalidated It

- Compensating control 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Compensating control 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Caution 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.
