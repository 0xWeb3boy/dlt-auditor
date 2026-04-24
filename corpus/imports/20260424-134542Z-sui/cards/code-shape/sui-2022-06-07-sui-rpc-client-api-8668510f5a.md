# Code-Shape Card

## Metadata

- ID: `sui-2022-06-07-sui-rpc-client-api-8668510f5a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-integrity-hardening`

## Code Shape Summary

- The patch changes Sui checkpoint handling by adding a previous checkpoint digest to checkpoint summary/proposal construction paths and by comparing fetched checkpoint contents against content_digest instead of the whole checkpoint digest.

## Search Motifs

- state-transition-invariant enforced after parsing but before rpc-client-api state mutation
- rpc-client-api handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Carry the previous checkpoint digest through checkpoint creation/proposal paths and validate fetched detail data against the digest field that commits to that detail data.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
