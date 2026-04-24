# Code-Shape Card

## Metadata

- ID: `sui-2026-02-27-sui-transaction-processing-48d0a9bce8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-transaction-panic`

## Code Shape Summary

- Consolidate tx checking in signing and simulate (#25624) appears to strengthen state integrity in the transaction-processing path of sui. The strongest evidence spans `crates/sui-core/src/authority.rs` and `crates/sui-core/src/authority.rs`.

## Search Motifs

- input-validation enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The transaction-processing sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- The fix pattern is to tighten the sensitive transaction-processing control path so the key invariant is enforced before downstream work continues.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
