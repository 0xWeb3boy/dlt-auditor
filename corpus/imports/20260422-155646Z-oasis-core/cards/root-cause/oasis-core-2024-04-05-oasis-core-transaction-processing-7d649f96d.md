# Root-Cause Card

## Metadata

- ID: `oasis-core-2024-04-05-oasis-core-transaction-processing-7d649f96d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-gas-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `gas-accounting`

## Violated Invariant

- Invariant: These consensus handlers are expected to account for operation-specific gas before deeper processing, and simulation should reflect the same accounting for fee estimation.

## Trust Boundary

- Boundary: `user->mempool`

## Attack Surface

- Entrypoint type: `transaction-handler`
- Sensitive sink: `state-mutating transaction execution without full fee charge`

## Impact Pattern

- Primary impact: `resource-exhaustion`
- Secondary impact: `denial-of-service`

## Short Reusable Lesson

- These consensus handlers are expected to account for operation-specific gas before deeper processing, and simulation should reflect the same accounting for fee estimation. In this pattern, several key manager transaction handlers appear to have omitted explicit per-operation gas charging at the start of handler execution. The fix standardizes that charging pattern and aligns simulation behavior with live gas accounting. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
