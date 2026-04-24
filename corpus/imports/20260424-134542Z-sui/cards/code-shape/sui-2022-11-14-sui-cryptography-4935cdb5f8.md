# Code-Shape Card

## Metadata

- ID: `sui-2022-11-14-sui-cryptography-4935cdb5f8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-epoch-binding`

## Code Shape Summary

- The patch changes Sui authority signatures from signing only the message value to signing the value plus EpochId, and updates checkpoint fragment verification to supply the current committee epoch.

## Search Motifs

- state-transition-invariant enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Add protocol-domain binding to signed bytes by including the epoch in both signing and verification inputs.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
