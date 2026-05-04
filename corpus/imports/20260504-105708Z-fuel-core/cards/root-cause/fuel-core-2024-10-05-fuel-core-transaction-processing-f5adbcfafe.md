# Root-Cause Card

## Metadata

- ID: `fuel-core-2024-10-05-fuel-core-transaction-processing-f5adbcfafe`
- Bug family: `resource_accounting_and_limits`
- Bug class: `graphql-query-complexity-accounting`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource-accounting`

## Violated Invariant

- GraphQL complexity formulas must charge nested resolvers according to the amount of storage and child work they can trigger.

## Trust Boundary

- Boundary: `unauthenticated-client->graphql-resource-budget`
- Entrypoint type: `rpc-handler`
- Sensitive sink: `GraphQL query scheduler and storage-backed resolvers`

## Attack Surface

- Send nested GraphQL queries selecting blocks, headers, transactions, or status fields.
- Choose child selections that multiply resolver work.

## Exploit Preconditions

- The API exposes complexity-limited GraphQL to untrusted or semi-trusted callers.
- Resolver annotations undercharge nested or repeated storage work.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `resource-exhaustion`
- Blast radius: `node-local`
- Severity guess: `medium`

## Short Reusable Lesson

- API query-cost models should approximate worst-case resolver fanout, not just direct storage reads.
