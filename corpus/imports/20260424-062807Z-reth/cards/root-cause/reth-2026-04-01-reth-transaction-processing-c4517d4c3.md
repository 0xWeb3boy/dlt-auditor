# Root-Cause Card

## Metadata

- ID: `reth-2026-04-01-reth-transaction-processing-c4517d4c3`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-corruption`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `per-call-resource-accounting`

## Violated Invariant

- Invariant: A precompile cache hit must not reuse caller-scoped gas-accounting state from an earlier execution. Cached entries may replay deterministic output bytes, reverted status, and regular gas cost, but the current call's gas limit and reservoir must remain authoritative.

## Trust Boundary

- Boundary: transaction execution/precompile call -> gas accounting state

## Attack Surface

- Entrypoint type: state-transition/precompile-execution
- Sensitive sink: gas reservoir, receipt, and execution accounting

## Impact Pattern

- Primary impact: gas-accounting-integrity
- Secondary impact: denial-of-service

## Short Reusable Lesson

- A precompile cache hit must not reuse caller-scoped gas-accounting state from an earlier execution. Cached entries may replay deterministic output bytes, reverted status, and regular gas cost, but the current call's gas limit and reservoir must remain authoritative.
