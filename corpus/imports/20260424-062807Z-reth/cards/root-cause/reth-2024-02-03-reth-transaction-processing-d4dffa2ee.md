# Root-Cause Card

## Metadata

- ID: `reth-2024-02-03-reth-transaction-processing-d4dffa2ee`
- Bug family: `resource_accounting_and_limits`
- Bug class: `improper-resource-limit-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-limit-accounting`

## Violated Invariant

- Invariant: The blob subpool should evict transactions whenever any configured capacity bound is exceeded, so that both the transaction-count limit and tracked-size limit are enforced.

## Trust Boundary

- Boundary: external transaction source -> mempool policy engine

## Attack Surface

- Entrypoint type: transaction-pool-handler
- Sensitive sink: mempool admission, eviction, or propagation decision

## Impact Pattern

- Primary impact: resource-exhaustion
- Secondary impact: denial-of-service

## Short Reusable Lesson

- The blob subpool should evict transactions whenever any configured capacity bound is exceeded, so that both the transaction-count limit and tracked-size limit are enforced.
