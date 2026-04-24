# Root-Cause Card

## Metadata

- ID: `bor-2026-03-19-bor-transaction-processing-7d6a68d8b`
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

- Primary impact: availability-impact
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The visible issue is inconsistent or previously missing range-budget enforcement on some RPC log/filter entry points, plus the need to normalize symbolic block numbers for the guard logic. The commit message suggests config pass-through was also involved, but that part is not directly shown in the provided hunks.
