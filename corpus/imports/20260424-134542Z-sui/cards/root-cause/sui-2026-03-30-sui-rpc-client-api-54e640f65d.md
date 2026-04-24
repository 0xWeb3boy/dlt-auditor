# Root-Cause Card

## Metadata

- ID: `sui-2026-03-30-sui-rpc-client-api-54e640f65d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-traffic-control-accounting`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: Every state transition that consumes resources or changes balances must update the corresponding accounting state exactly once and within protocol bounds.

## Trust Boundary

- Boundary: remote client/proxy request or response -> node API trust decision

## Attack Surface

- Entrypoint type: rpc-handler
- Sensitive sink: consuming validator CPU, memory, network, or execution budget

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The validator submit path previously returned zero traffic-control spam weight even when handling gasless transactions. The patch adds request-level spam-weight tracking, sets it to `Weight::one()` for transactions identified by `is_gasless_transaction()`, and returns the computed weight through the observed submit-response.
