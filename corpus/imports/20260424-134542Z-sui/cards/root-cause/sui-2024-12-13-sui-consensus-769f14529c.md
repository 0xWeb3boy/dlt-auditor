# Root-Cause Card

## Metadata

- ID: `sui-2024-12-13-sui-consensus-769f14529c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-control-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Untrusted work must be bounded, attributed, and charged or throttled before it can consume shared validator resources.

## Trust Boundary

- Boundary: validator-or-peer message -> consensus state machine

## Attack Surface

- Entrypoint type: consensus-message-handler
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: availability-hardening
- Secondary impact: context-dependent

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The patch adds writeback-cache backpressure and RPC overload rejection based on pending transaction count, with checkpoint-watermark state used to guard consensus pausing.
