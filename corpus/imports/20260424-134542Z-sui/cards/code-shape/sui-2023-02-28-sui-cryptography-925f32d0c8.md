# Code-Shape Card

## Metadata

- ID: `sui-2023-02-28-sui-cryptography-925f32d0c8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-metadata-validation`

## Code Shape Summary

- The patch adds centralized validator metadata verification before active validator metadata is used to construct Narwhal committee and worker-cache configuration.

## Search Motifs

- input-validation enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The cryptography sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Centralize validator metadata validation and require consensus-facing consumers to use the verified typed representation instead of raw metadata bytes.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
