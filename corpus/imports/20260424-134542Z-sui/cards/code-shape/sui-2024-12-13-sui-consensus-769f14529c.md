# Code-Shape Card

## Metadata

- ID: `sui-2024-12-13-sui-consensus-769f14529c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-control-hardening`

## Code Shape Summary

- The patch adds writeback-cache backpressure and RPC overload rejection based on pending transaction count, with checkpoint-watermark state used to guard consensus pausing.

## Search Motifs

- resource-accounting enforced after parsing but before consensus state mutation
- consensus handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Add configurable resource backpressure and retryable overload responses, with checkpoint-progress gating around consensus pausing.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
- The value is only advisory and is recomputed from canonical local consensus state before use.
