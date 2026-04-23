# Root-Cause Card

## Metadata

- ID: `reth-2026-04-01-reth-transaction-processing-c4517d4c3`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-accounting-corruption`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The evidence supports a correctness bug in production precompile-cache gas accounting: cache hits previously reused a cached `PrecompileOutputExt` wholesale, including its `GasTracker`, instead of rebuilding gas state from the current call. That establishes stale-state reuse and corrupted reservoir accounting on cache hits. The provided material does not, by itself, establish a concrete security impact beyond that accounting corruption.
