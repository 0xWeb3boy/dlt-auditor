# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-graphql-transactions-pagination-panic-32486`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `graphql-pagination-unreachable-panic`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `api-parameter-combination-validation`

## Violated Invariant

- Public RPC pagination must reject unsupported cursor/count combinations with an error instead of panicking.

## Trust Boundary

- Boundary: `public-rpc-user->node-process`
- Entrypoint type: `rpc-handler`
- Sensitive sink: `unreachable macro in transaction pagination`

## Attack Surface

- Send a GraphQL transactions query with cursor fields but no first or last count.
- Repeat the unauthenticated query against public RPC nodes.

## Exploit Preconditions

- Validation allows after/before without first/last.
- Resolver assumes one count is present and reaches unreachable!().

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `rpc-availability`
- Blast radius: `node-local`
- Severity guess: `medium`

## Short Reusable Lesson

- Public API code must treat every parameter combination as user-controlled, even when a branch looks unreachable internally.
