# Root-Cause Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-b1829ef95`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-hardening`
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

- Primary impact: availability
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The visible issue is missing or inconsistent pre-construction validation for block-range log queries in multiple RPC paths. The commit subject suggests a separate config pass-through problem for the range-limit setting, but that wiring is not shown in the supplied evidence.
