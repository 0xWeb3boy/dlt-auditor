# Root-Cause Card

## Metadata

- ID: `sui-2026-03-27-sui-storage-b889b4d1bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-amplification-control`
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

- Primary impact: resource-exhaustion
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch re-enables `defer_unpaid_amplification` for protocol version 120 on non-mainnet chains and restores capped benchmark traffic that exercises amplified submissions.
