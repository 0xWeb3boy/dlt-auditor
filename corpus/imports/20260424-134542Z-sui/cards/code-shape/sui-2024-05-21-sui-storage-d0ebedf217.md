# Code-Shape Card

## Metadata

- ID: `sui-2024-05-21-sui-storage-d0ebedf217`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-threshold-api-hardening`

## Code Shape Summary

- The evidence supports a cleanup or hardening of the bridge committee signature API, not a validated vulnerability fix. Callers no longer pass an explicit threshold to `request_committee_signatures`; the aggregator derives `action.approval_threshold()` internally. Existing shown callers already passed `action.

## Search Motifs

- signature-verification enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- alternate signed encodings accepted as equivalent
- missing epoch/domain/payload binding in verifier

## Typical Asymmetry

- The producer can vary signed bytes or context while the verifier accidentally treats distinct security domains as equivalent.

## Patch Pattern

- Centralize a security-sensitive derived parameter inside the API that consumes it, instead of requiring each caller to pass the value separately.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- The alternative encoding cannot be produced by an untrusted party or is normalized before verification.
