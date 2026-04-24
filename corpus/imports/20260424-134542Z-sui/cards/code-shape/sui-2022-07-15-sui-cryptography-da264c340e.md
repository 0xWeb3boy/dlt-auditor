# Code-Shape Card

## Metadata

- ID: `sui-2022-07-15-sui-cryptography-da264c340e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-response-verification`

## Code Shape Summary

- The patch is best classified as checkpoint response verification hardening. It adds centralized `CheckpointResponse::verify(&Committee)` and calls it before request-specific validation in the safe client, and it adds a guard for missing requested detail on signed or certified past checkpoints.

## Search Motifs

- state-transition-invariant enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Centralize response authentication at the remote-response trust boundary, then separately enforce request/response consistency and detail availability rules.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
