# Root-Cause Card

## Metadata

- ID: `sei-chain-2022-12-19-sei-chain-transaction-processing-e3373eba5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `liveness-failure`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `execution-resource-metering`

## Violated Invariant

- Invariant: Lifecycle-triggered contract execution must remain bounded by the parent block or transaction resource meter.

## Trust Boundary

- Boundary: module lifecycle hook -> Wasm contract execution engine

## Attack Surface

- Entrypoint type: beginblock-or-endblock-contract-callback
- Sensitive sink: executing contract sudo logic during block processing

## Impact Pattern

- Primary impact: liveness
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- Replace infinite metering in lifecycle-triggered Wasm execution with parent-limit-based gas metering, and handle expected out-of-gas panics at the Wasm sudo boundary. BeginBlock and EndBlock are liveness-sensitive protocol paths. Infinite gas metering around contract execution can undermine resource limits during block processing.
