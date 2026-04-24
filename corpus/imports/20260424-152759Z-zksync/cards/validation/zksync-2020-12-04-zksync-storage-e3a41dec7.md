# Validation Card

## Metadata

- ID: `zksync-2020-12-04-zksync-storage-e3a41dec7`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-prover-api-authentication`

## What Confirmed The Issue

- Server-side JWT/auth validation support is added.
- Prover clients are updated to generate and attach bearer tokens.
- The affected endpoints coordinate prover work.

## What Could Have Invalidated It

- A mandatory reverse proxy or network policy already authenticated every request.
- The added token is never checked by the server route handling the sensitive endpoint.

## Severity Guidance

- Expected impact band: `operator_service_integrity`
- Expected severity band: `medium_or_low`
- Rationale: Unauthenticated internal coordination APIs are important, but the evidence does not prove public exposure or proof validity compromise.

## False-Positive Cautions

- If the endpoint is bound only to localhost or protected by mTLS/firewall, severity is lower.
- Authentication additions do not prove proof forgery risk without a path from requests to accepted proofs.
