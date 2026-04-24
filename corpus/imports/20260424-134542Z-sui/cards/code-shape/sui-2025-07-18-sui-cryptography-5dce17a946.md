# Code-Shape Card

## Metadata

- ID: `sui-2025-07-18-sui-cryptography-5dce17a946`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-commitment-gap`

## Code Shape Summary

- The patch adds an `IndirectStateObserver` and conditionally folds observed indirect state into the additional consensus digest recorded in the consensus commit prologue.

## Search Motifs

- state-transition-invariant enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Thread an explicit observer through commit-processing paths that inspect derived state, hash the observed state deterministically, and include that hash in the consensus/prologue digest behind a protocol feature flag.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
