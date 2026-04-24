# Root-Cause Card

## Metadata

- ID: `reth-2024-02-02-reth-transaction-processing-72b7caa4c`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-limit-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-limit-accounting`

## Violated Invariant

- Invariant: When truncating the parked subpool, the implementation should enforce the configured pool limit across all tracked dimensions used by `SubPoolLimit`, including transaction count and aggregate size, rather than count alone.

## Trust Boundary

- Boundary: external transaction source -> mempool policy engine

## Attack Surface

- Entrypoint type: transaction-pool-handler
- Sensitive sink: mempool admission, eviction, or propagation decision

## Impact Pattern

- Primary impact: resource-exhaustion
- Secondary impact: denial-of-service

## Short Reusable Lesson

- When truncating the parked subpool, the implementation should enforce the configured pool limit across all tracked dimensions used by `SubPoolLimit`, including transaction count and aggregate size, rather than count alone.
