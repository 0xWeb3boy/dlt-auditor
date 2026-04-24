# Code-Shape Card

## Metadata

- ID: `sui-2023-03-01-sui-transaction-processing-7b60006a26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- Add ProtocolConfig limits for various attributes of input transactions. (#8557) appears to strengthen state integrity in the transaction-processing path of sui. The strongest evidence spans `crates/sui-types/src/messages.rs` and `crates/sui-types/src/messages.rs`.

## Search Motifs

- resource-accounting enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- The fix pattern is to tighten the sensitive transaction-processing control path so the key invariant is enforced before downstream work continues.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
