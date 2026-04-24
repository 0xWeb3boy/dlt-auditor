# Root-Cause Card

## Metadata

- ID: `sui-2022-05-03-sui-transaction-processing-601889c18e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
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

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The evidence supports a conservative security-hardening finding for Sui authority follower batch streaming. The strongest grounded change is resource-control hardening: authority-side request bounds were added, and SafeClient now tracks streamed item count with an inline comment identifying the guard as protection against.
