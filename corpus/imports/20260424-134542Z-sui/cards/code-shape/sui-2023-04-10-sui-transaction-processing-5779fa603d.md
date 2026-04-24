# Code-Shape Card

## Metadata

- ID: `sui-2023-04-10-sui-transaction-processing-5779fa603d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `monetary-accounting-invariant-hardening`

## Code Shape Summary

- The patch adds configuration plumbing for an expensive deep per-transaction SUI conservation check in Sui transaction execution.

## Search Motifs

- resource-accounting enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The transaction-processing sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Add an explicit opt-in expensive invariant guard to node configuration and thread the guard through the transaction execution path, while enabling it automatically in debug builds.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
