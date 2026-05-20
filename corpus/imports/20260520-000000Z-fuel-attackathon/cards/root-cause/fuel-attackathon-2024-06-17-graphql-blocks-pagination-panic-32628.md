# Root-Cause Card

## Metadata

- ID: `fuel-attackathon-2024-06-17-graphql-blocks-pagination-panic-32628`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `graphql-pagination-unreachable-panic`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `api-parameter-combination-validation`

## Violated Invariant

- Public block queries must validate cursor/count combinations before entering pagination logic.

## Trust Boundary

- Boundary: `public-rpc-user->node-process`
- Entrypoint type: `rpc-handler`
- Sensitive sink: `unreachable macro in block pagination`

## Attack Surface

- Send a GraphQL blocks query with after or before but no first or last.
- Target any node exposing the public GraphQL API.

## Exploit Preconditions

- The validation layer accepts cursor-only pagination.
- The pagination helper panics when neither first nor last is present.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `rpc-availability`
- Blast radius: `node-local`
- Severity guess: `medium`

## Short Reusable Lesson

- Shared pagination helpers should encode API invariants once so every resolver rejects unsafe combinations consistently.
