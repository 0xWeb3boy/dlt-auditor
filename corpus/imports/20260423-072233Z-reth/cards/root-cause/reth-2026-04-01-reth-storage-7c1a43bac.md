# Root-Cause Card

## Metadata

- ID: `reth-2026-04-01-reth-storage-7c1a43bac`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-state-reuse`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `per-invocation-resource-accounting-isolation`

## Violated Invariant

- Invariant: Cached execution outputs may reuse stable bytes and deterministic cost, but must not replay live gas or reservoir accounting from a different invocation.

## Trust Boundary

- Boundary: Cached precompile result crossing into the current caller execution frame.

## Attack Surface

- Entrypoint type: precompile-cache-hit
- Sensitive sink: GasTracker, reservoir, and state-gas accounting used by execution.

## Impact Pattern

- Primary impact: Cache hits preserve the current caller reservoir and gas limit.
- Secondary impact: Precompile caching no longer overwrites live execution accounting with stale state.

## Short Reusable Lesson

- A precompile cache hit reused a cached output object that embedded stale gas and reservoir state. The patch passes the current caller gas and reservoir into reconstruction and reuses only stable cached output data and regular gas cost.
