# Root-Cause Card

## Metadata

- ID: `bor-2026-03-18-bor-transaction-processing-858c6ae6d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `arithmetic bounds and resource accounting`

## Violated Invariant

- Invariant: Attacker-controlled input must be bounded and rejected before it can drive unbounded allocation, expensive processing, queue growth, or process termination.

## Trust Boundary

- Boundary: external RPC client to node service boundary

## Attack Surface

- Entrypoint type: public or administrative RPC method
- Sensitive sink: backend state access, privileged API behavior, or response serialization

## Impact Pattern

- Primary impact: availability
- Secondary impact: resource-exhaustion

## Short Reusable Lesson

- The visible issue is inconsistent or missing enforcement of a configured block-range limit in several RPC log-filter entry points. The commit subject also mentions config pass-through, but the provided evidence does not show that wiring bug directly.
