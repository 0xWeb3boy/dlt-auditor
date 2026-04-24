# Code-Shape Card

## Metadata

- ID: `sui-2022-02-06-sui-staking-db9ee35c05`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `byzantine-authority-robustness`

## Code Shape Summary

- The draft's staking and confirmed vulnerability framing is unsupported. The patch is best described as a FastPay client-authority synchronization robustness and API semantics change: it adds generic authority map/reduce logic, changes ObjectInfoResponse semantics, records deleted-object state in parent_sync, and avoids.

## Search Motifs

- authorization enforced after parsing but before staking state mutation
- staking handler accepts externally supplied protocol data
- object authority derived from request fields
- privileged mutation reachable before ownership check

## Typical Asymmetry

- The caller controls identifiers or objects that the sink treats as authority unless ownership is checked first.

## Patch Pattern

- Make synchronization semantics explicit and tolerate incomplete or failing per-authority responses instead of assuming every successful response has the same optional fields populated.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A later mandatory ownership or capability check rejects the request before any state change.
