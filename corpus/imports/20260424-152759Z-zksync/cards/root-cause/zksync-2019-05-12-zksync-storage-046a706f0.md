# Root-Cause Card

## Metadata

- ID: `zksync-2019-05-12-zksync-storage-046a706f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-missing-storage-record`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `absent-state-handling`

## Violated Invariant

- Invariant: Request-selected storage objects must be treated as optional at API boundaries; a missing canonical record should produce a structured error, not a panic.

## Trust Boundary

- Boundary: Unauthenticated HTTP request parameter crosses into a database-backed block lookup and response builder.

## Attack Surface

- Entrypoint type: `public_read_api_path_parameter`
- Sensitive sink: API handler availability and COMMIT-operation block-detail reconstruction

## Impact Pattern

- Primary impact: availability loss through panic on absent state
- Secondary impact: reliability hardening at storage/API boundary

## Short Reusable Lesson

- A read API handler used a request-derived block id to fetch a required COMMIT operation and called a panic path when the record was absent. The reusable shape is an infallible unwrap/expect at an external API to storage boundary, fixed by returning a typed not-found response before unwrapping.
