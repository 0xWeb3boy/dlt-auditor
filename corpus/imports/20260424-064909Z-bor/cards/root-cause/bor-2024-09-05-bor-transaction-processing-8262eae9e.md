# Root-Cause Card

## Metadata

- ID: `bor-2024-09-05-bor-transaction-processing-8262eae9e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-context-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- An API layering mismatch: the Bor code needed a read bound to a specific state.StateDB, but it used a convenience wrapper that discarded that state and defaulted to a different execution context.
