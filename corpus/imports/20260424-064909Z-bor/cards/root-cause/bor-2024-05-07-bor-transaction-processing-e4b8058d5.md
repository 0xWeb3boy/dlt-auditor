# Root-Cause Card

## Metadata

- ID: `bor-2024-05-07-bor-transaction-processing-e4b8058d5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource limit and input validity enforcement`

## Violated Invariant

- Invariant: Attacker-controlled input must be bounded and rejected before it can drive unbounded allocation, expensive processing, queue growth, or process termination.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- A request-cost dimension was left unchecked: FeeHistory accepted an unbounded number of reward percentiles in the shown pre-patch code, even though block count was already bounded.
