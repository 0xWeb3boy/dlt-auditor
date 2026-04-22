# Validation Card

## Metadata

- ID: `oasis-core-2023-07-31-oasis-core-staking-67711fa42`
- Bug family: `staking_registry_and_accountability`
- Bug class: `proposer-liveness-accounting-gap`

## What Confirmed The Issue

- Evidence 1: The patch records missed proposals when a valid proposer-timeout transaction is processed, and it adds 'TransactionSchedulerIdx' so scheduler identity can be expressed as a committee-member index instead of only as a position within the filtered worker slice. This makes the new proposer-timeout accounting usable by later liveness evaluation code.
- Evidence 2: The source finding states the invariant explicitly: If proposer liveness is evaluated, proposer timeout events must be attributed to the intended committee member so later liveness processing uses consistent per-member statistics.

## What Could Have Invalidated It

- Compensating control 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Compensating control 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Caution 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.
