# Code-Shape Card

## Metadata

- ID: `sui-2022-10-04-sui-storage-93f796a5cc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-resource-control-hardening`

## Code Shape Summary

- The patch improves consensus adapter resilience by adding user-transaction backpressure before consensus submission, using a fixed 60 second certificate sequencing timeout, reducing listener queue capacity, adding inflight metrics, and improving capacity diagnostics.

## Search Motifs

- resource-accounting enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Add bounded resource controls and conservative timeout configuration around consensus-adapter ingress, with diagnostic improvements for capacity pressure.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
- The value is only advisory and is recomputed from canonical local consensus state before use.
