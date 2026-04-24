# Root-Cause Card

## Metadata

- ID: `sui-2022-10-04-sui-storage-93f796a5cc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-resource-control-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Untrusted work must be bounded, attributed, and charged or throttled before it can consume shared validator resources.

## Trust Boundary

- Boundary: executed effects or checkpoint data -> authenticated persistent state

## Attack Surface

- Entrypoint type: state-transition-storage-update
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: denial-of-service-mitigation
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch improves consensus adapter resilience by adding user-transaction backpressure before consensus submission, using a fixed 60 second certificate sequencing timeout, reducing listener queue capacity, adding inflight metrics, and improving capacity diagnostics.
