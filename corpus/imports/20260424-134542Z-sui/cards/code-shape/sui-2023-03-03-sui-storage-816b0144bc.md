# Code-Shape Card

## Metadata

- ID: `sui-2023-03-03-sui-storage-816b0144bc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-invariant-hardening`

## Code Shape Summary

- The patch is best characterized as SUI accounting hardening, not a proven vulnerability fix. The grounded evidence shows TemporaryStore::check_sui_conserved was adjusted to compute written-output SUI through TemporaryStore state instead of only the backing store, and supporting GetModule/ObjectStore trait implementations were.

## Search Motifs

- resource-accounting enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The storage sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Run or enable invariant checking at the point where required gas/accounting state is available, and make the check resolve data through the execution-state abstraction rather than only persistent backing storage.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
