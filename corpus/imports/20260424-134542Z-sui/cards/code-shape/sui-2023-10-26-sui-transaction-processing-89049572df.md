# Code-Shape Card

## Metadata

- ID: `sui-2023-10-26-sui-transaction-processing-89049572df`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-control-hardening`

## Code Shape Summary

- The patch adds cost-aware execution for selected Sui GraphQL RPC PostgreSQL-backed data-provider queries and improves SQL placeholder normalization used for cost estimation.

## Search Motifs

- resource-accounting enforced after parsing but before transaction-processing state mutation
- transaction-processing handler accepts externally supplied protocol data
- unbounded loop/cache/retry path driven by remote input
- missing per-client or per-digest resource attribution

## Typical Asymmetry

- Cheap attacker-controlled submissions can force repeated validator work unless the path charges, attributes, or throttles before the expensive operation.

## Patch Pattern

- Route selected database-backed GraphQL RPC queries through a centralized cost-aware execution wrapper and make SQL placeholder normalization more context-sensitive for cost estimation.

## False Match Warnings

- Equivalent validation, charging, or authorization is already enforced on every path before the shown sink.
- The changed path handles only local test fixtures, telemetry, or unreachable migration code.
- A separate hard cap, authenticated quota, or upstream rate limit makes repeated work impossible.
