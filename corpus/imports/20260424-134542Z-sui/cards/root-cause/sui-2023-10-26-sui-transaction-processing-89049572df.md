# Root-Cause Card

## Metadata

- ID: `sui-2023-10-26-sui-transaction-processing-89049572df`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-control-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Untrusted work must be bounded, attributed, and charged or throttled before it can consume shared validator resources.

## Trust Boundary

- Boundary: submitted transaction or validator response -> execution/effects pipeline

## Attack Surface

- Entrypoint type: transaction-handler
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch adds cost-aware execution for selected Sui GraphQL RPC PostgreSQL-backed data-provider queries and improves SQL placeholder normalization used for cost estimation.
