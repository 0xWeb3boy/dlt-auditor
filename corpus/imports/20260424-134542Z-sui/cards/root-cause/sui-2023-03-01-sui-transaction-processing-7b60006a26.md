# Root-Cause Card

## Metadata

- ID: `sui-2023-03-01-sui-transaction-processing-7b60006a26`
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
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. Add ProtocolConfig limits for various attributes of input transactions. (#8557) appears to strengthen state integrity in the transaction-processing path of sui. The strongest evidence spans `crates/sui-types/src/messages.rs` and `crates/sui-types/src/messages.rs`.
