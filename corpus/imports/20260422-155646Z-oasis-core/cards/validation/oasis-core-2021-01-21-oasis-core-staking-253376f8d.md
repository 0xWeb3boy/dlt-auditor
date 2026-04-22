# Validation Card

## Metadata

- ID: `oasis-core-2021-01-21-oasis-core-staking-253376f8d`
- Bug family: `staking_registry_and_accountability`
- Bug class: `insufficient-validator-slashing-enforcement`

## What Confirmed The Issue

- Evidence 1: The patch wires per-runtime slashing settings into runtime configuration and API validation, then adjusts slashing and transfer helpers so stale-evidence or empty-pool cases do not abort the operation path. The visible changes look like support and robustness work for runtime slashing rather than standalone proof of an exploitable bug.
- Evidence 2: The source finding states the invariant explicitly: Runtime misbehavior penalties should be representable in the runtime staking parameters and processed without failing on expected edge cases such as stale evidence or zero available funds.

## What Could Have Invalidated It

- Compensating control 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Compensating control 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if consensus rules or earlier checks make the edge case unreachable for live validators, entities, or runtimes.
- Caution 2: Not a match if the patch only improves reporting or accounting visibility without changing stake, slashing, or selection state.
