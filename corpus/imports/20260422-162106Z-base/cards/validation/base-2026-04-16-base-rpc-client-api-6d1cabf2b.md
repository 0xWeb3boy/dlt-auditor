# Validation Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-6d1cabf2b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incorrect-fraud-challenge-validation`

## What Confirmed The Issue

- Evidence 1: Commit message states the old logic could cause the challenger to skip nullifying a fraudulent ZK challenge.
- Evidence 2: `process_fraudulent_zk_challenge` now fetches only `intermediate_output_root(game_address, challenged_index)` instead of using all intermediate roots.

## What Could Have Invalidated It

- Compensating control 1: This supports a security-relevant hardening in off-chain challenger dispute handling.
- Compensating control 2: It does not establish a confirmed exploitable vulnerability from the patch alone.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: This supports a security-relevant hardening in off-chain challenger dispute handling.
- Caution 2: It does not establish a confirmed exploitable vulnerability from the patch alone.
