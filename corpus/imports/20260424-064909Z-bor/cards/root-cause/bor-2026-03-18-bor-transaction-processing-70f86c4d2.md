# Root-Cause Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-70f86c4d2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-rpc-range-limit-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource limit and input validity enforcement`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: availability
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- Range-limit enforcement was not consistently applied in the RPC filter code paths handling block-range log queries, and symbolic block selectors needed explicit normalization for that validation logic.
