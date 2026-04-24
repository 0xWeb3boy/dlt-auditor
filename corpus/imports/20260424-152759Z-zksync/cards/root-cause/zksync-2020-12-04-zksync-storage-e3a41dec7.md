# Root-Cause Card

## Metadata

- ID: `zksync-2020-12-04-zksync-storage-e3a41dec7`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-prover-api-authentication`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `service-to-service-authentication`

## Violated Invariant

- Invariant: Coordinator APIs that assign prover work or accept prover responses should authenticate service clients before exposing privileged coordination state.

## Trust Boundary

- Boundary: Network client crosses into prover server/witness generator coordination endpoints.

## Attack Surface

- Entrypoint type: `internal_service_http_api`
- Sensitive sink: prover job assignment, result submission, and coordination state

## Impact Pattern

- Primary impact: unauthorized access to prover coordination API
- Secondary impact: pipeline resource abuse or integrity confusion

## Short Reusable Lesson

- The patch adds bearer-token/JWT validation to prover server/client coordination, and clients attach generated bearer tokens. The reusable shape is a privileged internal service API that previously trusted network reachability or caller convention instead of request authentication.
