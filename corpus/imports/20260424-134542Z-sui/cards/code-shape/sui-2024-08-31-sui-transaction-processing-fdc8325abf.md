# Code-Shape Card

## Metadata

- ID: `sui-2024-08-31-sui-transaction-processing-fdc8325abf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## Code Shape Summary

- The patch is best characterized as GraphQL RPC availability hardening for oversized transaction-bearing requests. The commit text states that mutation and dry-run transaction payloads can be much larger than ordinary query payloads and adds a max_tx_payload_size derived from protocol max_tx_bytes with Base64 overhead.

## Search Motifs

- resource-accounting enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Introduce a specialized resource budget for transaction-bearing GraphQL payloads, derive it from the protocol transaction byte limit plus encoding overhead, enforce it during GraphQL limit checking, and fail closed when the budget is exceeded.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
