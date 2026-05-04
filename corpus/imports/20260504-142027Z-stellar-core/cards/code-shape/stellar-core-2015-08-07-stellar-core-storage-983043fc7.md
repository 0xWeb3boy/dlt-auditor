# Code-Shape Card

## Metadata

- ID: `stellar-core-2015-08-07-stellar-core-storage-983043fc7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-consensus-configuration`

## Code Shape Summary

- The config loader accepted an absolute quorum threshold, then later code added bounded percentages, derived thresholds, failure-safety fields, and unsafe-mode validation.

## Search Motifs

- raw THRESHOLD parsed into quorum set
- THRESHOLD_PERCENT bounded 1..100
- FAILURE_SAFETY equals zero without unsafe opt in
- qset.threshold derived from validator count

## Typical Asymmetry

- The code had a validation or resource-control assumption at one boundary, but a later authoritative boundary or helper accepted broader state than the invariant allowed.
- The risky input was ordinary protocol data or operator configuration, so the bug shape looks like normal processing until the missing property is checked against the sensitive sink.

## Patch Pattern

- Replace raw consensus threshold input with bounded derived configuration and add startup validation for unsafe safety settings.

## False Match Warnings

- Explicit testnet or unsafe modes may intentionally allow weak quorum settings.
- Configuration mistakes are not remote vulnerabilities unless attackers can influence deployment config.
- Quorum-analysis tools may warn rather than reject by design.
