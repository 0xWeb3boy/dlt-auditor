# Code-Shape Card

## Metadata

- ID: `zksync-2020-12-04-zksync-storage-e3a41dec7`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-prover-api-authentication`

## Code Shape Summary

- The patch adds bearer-token/JWT validation to prover server/client coordination, and clients attach generated bearer tokens. The reusable shape is a privileged internal service API that previously trusted network reachability or caller convention instead of request authentication.

## Search Motifs

- AuthTokenValidator or JWT validation added to server route setup
- prover client starts attaching Authorization: Bearer token
- shared secret/auth config introduced for service-to-service calls

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Introduce shared-secret token creation on clients and token validation middleware/server checks on prover coordination endpoints.

## False Match Warnings

- If the endpoint is bound only to localhost or protected by mTLS/firewall, severity is lower.
- Authentication additions do not prove proof forgery risk without a path from requests to accepted proofs.
- Client-token plumbing alone is incomplete unless server validation is active.
