# Root-Cause Card

## Metadata

- ID: `sui-2024-06-26-sui-rpc-client-api-a025ca0517`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `traffic-control-accounting-gap`
- Confidence tier: `tier_b_likely`

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

- Primary impact: resource-abuse
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- Input validation should establish the invariant required by the sink, not merely that the input is syntactically parseable. The supported finding is traffic-controller security hardening, not serialization or state-representation repair. The patch threads an explicit spam/accounting weight through authority service responses so successful gasless work can be counted by traffic-control logic.
