# Root-Cause Card

## Metadata

- ID: `fuel-core-2025-09-15-fuel-core-transaction-processing-d526593aff`
- Bug family: `resource_accounting_and_limits`
- Bug class: `graphql-query-complexity-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- Paginated API cost formulas must multiply per-item storage and child-selection work by the requested page size.

## Trust Boundary

- Boundary: `unauthenticated-client->graphql-resource-budget`
- Entrypoint type: `rpc-handler`
- Sensitive sink: `paginated transaction/message resolvers and query cost limiter`

## Attack Surface

- Submit GraphQL queries with large first/page-size values and expensive child selections.
- Repeat undercharged queries within normal request limits.

## Exploit Preconditions

- Pagination cost formula adds storage cost once instead of per returned item.
- Endpoint relies on complexity accounting for resource protection.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `resource-exhaustion`
- Blast radius: `node-local`
- Severity guess: `medium`

## Short Reusable Lesson

- Cost formulas for paginated APIs must charge per returned item, including nested child work and backing-store reads.
