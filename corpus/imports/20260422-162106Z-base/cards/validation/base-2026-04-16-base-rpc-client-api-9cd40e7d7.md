# Validation Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-9cd40e7d7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-challenge-validation`

## What Confirmed The Issue

- Evidence 1: Commit message describes a case where the challenger would skip nullifying a fraudulent ZK challenge because an earlier unrelated root was invalid.
- Evidence 2: `process_fraudulent_zk_challenge` was changed to fetch `intermediate_output_root(game_address, challenged_index)` and validate only that challenged root.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: the old challenger logic could mis-handle fraudulent ZK challenges by consulting unrelated intermediate roots.
- Compensating control 2: Supported claim: the fix narrows validation to the challenged root and strengthens dispute-decision correctness.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: the old challenger logic could mis-handle fraudulent ZK challenges by consulting unrelated intermediate roots.
- Caution 2: Supported claim: the fix narrows validation to the challenged root and strengthens dispute-decision correctness.
