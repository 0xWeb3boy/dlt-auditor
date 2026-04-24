# Code-Shape Card

## Metadata

- ID: `sui-2022-11-08-sui-storage-d8fef9cd19`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ownership-invariant-enforcement`

## Code Shape Summary

- The patch changes Sui's native shared-object transfer path from an unconditional successful transfer record into a classified transfer result. `share_object` now rejects `OwnerChanged` with `E_SHARED_NON_NEW_OBJECT`, enforcing that non-new objects are not converted into shared ownership.

## Search Motifs

- authorization enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- object authority derived from request fields
- privileged mutation reachable before ownership check

## Typical Asymmetry

- The caller controls identifiers or objects that the sink treats as authority unless ownership is checked first.

## Patch Pattern

- Return structured classification from the lower-level transfer routine and enforce the ownership invariant at the native shared-object API boundary.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A later mandatory ownership or capability check rejects the request before any state change.
