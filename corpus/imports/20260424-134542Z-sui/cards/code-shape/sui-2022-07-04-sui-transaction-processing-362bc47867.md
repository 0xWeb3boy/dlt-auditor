# Code-Shape Card

## Metadata

- ID: `sui-2022-07-04-sui-transaction-processing-362bc47867`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-response-handling`

## Code Shape Summary

- The patch hardens Sui authority sync fetching for checkpoints and finalized cert/effects by carrying known authority sets into aggregator fetch APIs. The evidence supports an availability and strict-response hardening claim, not a proven consensus safety break, invalid-certificate acceptance bug, or asset-loss vulnerability.

## Search Motifs

- input-validation enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- validation split across helper and sink
- error path treats malformed data as ordinary state

## Typical Asymmetry

- The transaction-processing sink assumes a property that was only partially established by earlier helper code.

## Patch Pattern

- Thread known authority sets from prior protocol evidence into artifact-fetch APIs, and centralize stricter retry/refusal handling in the aggregator rather than relying on ad hoc caller-side fetch logic.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
