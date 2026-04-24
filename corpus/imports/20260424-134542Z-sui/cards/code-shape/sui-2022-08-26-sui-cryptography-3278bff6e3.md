# Code-Shape Card

## Metadata

- ID: `sui-2022-08-26-sui-cryptography-3278bff6e3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-error-misclassification`

## Code Shape Summary

- The patch fixes security-relevant error misclassification in the Narwhal consensus handling path. The prior design used broad SuiError/FragmentInternalError classification to decide whether consensus execution should continue or stop.

## Search Motifs

- state-transition-invariant enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- state transition lacks epoch/checkpoint/quorum binding
- consensus output consumed without local invariant recheck

## Typical Asymmetry

- Remote or cross-epoch data may look structurally valid while not being bound to the local finalized state the consumer assumes.

## Patch Pattern

- Replace broad type-based error classification in consensus handling with explicit domain-specific error variants that encode whether a failure came from untrusted input verification or local node processing.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The value is only advisory and is recomputed from canonical local consensus state before use.
