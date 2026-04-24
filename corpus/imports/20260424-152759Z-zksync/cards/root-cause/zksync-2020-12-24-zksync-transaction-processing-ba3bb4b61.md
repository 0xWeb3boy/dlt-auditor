# Root-Cause Card

## Metadata

- ID: `zksync-2020-12-24-zksync-transaction-processing-ba3bb4b61`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `authentication-middleware-enforcement`

## Violated Invariant

- Invariant: A sensitive service API must actually install its authentication middleware on the route tree, not merely construct a validator object nearby.

## Trust Boundary

- Boundary: Network HTTP request crosses into witness generator/prover coordination service.

## Attack Surface

- Entrypoint type: `internal_service_http_api`
- Sensitive sink: prover-server coordination endpoints guarded by AuthTokenValidator

## Impact Pattern

- Primary impact: unauthenticated access to privileged service API
- Secondary impact: pipeline disruption or unauthorized coordination actions

## Short Reusable Lesson

- The patch restores Actix authentication middleware by changing a commented-out wrap(auth) into an active route wrapper. The reusable shape is security middleware constructed in code but not attached to the application that serves privileged endpoints.
