# Code-Shape Card

## Metadata

- ID: `sui-2026-03-27-sui-storage-b889b4d1bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-amplification-control`

## Code Shape Summary

- The patch re-enables `defer_unpaid_amplification` for protocol version 120 on non-mainnet chains and restores capped benchmark traffic that exercises amplified submissions.

## Search Motifs

- resource-accounting enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Enable an existing protocol-gated resource-control feature for selected non-mainnet networks and add bounded benchmark traffic to exercise it.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
