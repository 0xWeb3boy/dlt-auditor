# Root-Cause Card

## Metadata

- ID: `reth-2024-02-02-reth-transaction-processing-72b7caa4c`
- Bug family: `resource_accounting_and_limits`
- Bug class: `resource-limit-enforcement`
- Confidence tier: `tier_b_likely`

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

- The supplied diff supports a correctness fix in parked-pool truncation: the code now enforces the full pool-limit predicate using both count and size, whereas before it only used transaction count. That is grounded as a resource-control bug in mempool eviction logic. The evidence does not establish a concrete security vulnerability, exploit path, crash, or protocol-integrity failure.
