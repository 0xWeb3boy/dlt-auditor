# Root-Cause Card

## Metadata

- ID: `bor-2026-03-05-bor-consensus-26dc364ff`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic bounds and resource accounting`

## Violated Invariant

- Invariant: Resource and value accounting must use checked arithmetic and type ranges that cannot wrap, truncate, or undercharge attacker-controlled work.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- Missing range validation for block-height values and trust in persisted lock metadata that could be outside the safe block-number range used by later logic.
