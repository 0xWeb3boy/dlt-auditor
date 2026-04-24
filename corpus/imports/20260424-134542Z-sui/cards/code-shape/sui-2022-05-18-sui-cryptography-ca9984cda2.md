# Code-Shape Card

## Metadata

- ID: `sui-2022-05-18-sui-cryptography-ca9984cda2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-input-validation`

## Code Shape Summary

- The evidence supports a security-hardening classification for shared-object consensus input validation. The patch adds a local certificate.contains_shared_object() guard before shared-object consensus handling continues.

## Search Motifs

- state-transition-invariant enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Add an explicit validation guard at the consensus execution boundary and fail closed with a typed error when the certified transaction does not satisfy the shared-object invariant.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
