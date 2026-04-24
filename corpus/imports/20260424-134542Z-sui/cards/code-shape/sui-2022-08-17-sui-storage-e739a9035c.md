# Code-Shape Card

## Metadata

- ID: `sui-2022-08-17-sui-storage-e739a9035c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-retry-resource-control`

## Code Shape Summary

- The patch allows online retry of interrupted transactions, but moves retry accounting into the WAL begin path and rejects retries above `MAX_TX_RECOVERY_RETRY`. The evidence supports security-relevant resource-control hardening against poison-pill or crash-loop style retries, but not a confirmed exploitable vulnerability.

## Search Motifs

- resource-accounting enforced after parsing but before storage state mutation
- storage handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Centralize retry accounting in the guarded transaction-begin path and enforce a maximum retry limit before transaction execution continues.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
