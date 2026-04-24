# Code-Shape Card

## Metadata

- ID: `sui-2026-03-30-sui-rpc-client-api-54e640f65d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-traffic-control-accounting`

## Code Shape Summary

- The validator submit path previously returned zero traffic-control spam weight even when handling gasless transactions. The patch adds request-level spam-weight tracking, sets it to `Weight::one()` for transactions identified by `is_gasless_transaction()`, and returns the computed weight through the observed submit-response.

## Search Motifs

- resource-accounting enforced after parsing but before rpc-client-api state mutation
- rpc-client-api handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Add explicit traffic-control accounting state for the request, update it when a gasless transaction is observed, and propagate the computed value through all relevant return paths instead of returning a constant zero.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
