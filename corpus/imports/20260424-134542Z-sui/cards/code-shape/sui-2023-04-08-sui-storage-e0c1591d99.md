# Code-Shape Card

## Metadata

- ID: `sui-2023-04-08-sui-storage-e0c1591d99`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-object-digest-validation`

## Code Shape Summary

- The patch hardens Sui JSON-RPC `balanceChanges` construction by carrying object digests into the coin-fetching path and asserting that locally fetched coin objects match those digests before their contents are used. The evidence supports an RPC reporting integrity fix for stale or inconsistent local object reads.

## Search Motifs

- input-validation enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The storage sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Thread authenticated object identity material through derived RPC reporting code and validate local-store reads against it before using object contents for derived balance reporting.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
