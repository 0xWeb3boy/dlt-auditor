# Validation Card

## Metadata

- ID: `base-2026-04-16-base-rpc-client-api-8f939340a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-confirmation-depth`

## What Confirmed The Issue

- Evidence 1: The commit adds a verifier-specific L1 confirmation depth setting for derivation.
- Evidence 2: The watcher now conditionally derives from `head - verifier_l1_confs` instead of always using the latest head.

## What Could Have Invalidated It

- Compensating control 1: This supports consensus-safety hardening, not a proven vulnerability remediation.
- Compensating control 2: The evidence does not support the original `rpc-client-api` or serialization-focused framing.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: This supports consensus-safety hardening, not a proven vulnerability remediation.
- Caution 2: The evidence does not support the original `rpc-client-api` or serialization-focused framing.
