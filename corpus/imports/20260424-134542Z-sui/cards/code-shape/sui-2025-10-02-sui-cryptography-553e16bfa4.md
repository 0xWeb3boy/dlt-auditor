# Code-Shape Card

## Metadata

- ID: `sui-2025-10-02-sui-cryptography-553e16bfa4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- The patch is best treated as bridge node API input-validation and availability hardening. The strongest evidence is the new `validate_list_size` helper in `server/mod.rs`, whose comment explicitly says it prevents DoS during u8 conversion in encoding.

## Search Motifs

- input-validation enforced after parsing but before cryptography state mutation
- cryptography handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The cryptography sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Add explicit bounds checks at the bridge API input boundary and propagate encoding failures through fallible conversion APIs.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
