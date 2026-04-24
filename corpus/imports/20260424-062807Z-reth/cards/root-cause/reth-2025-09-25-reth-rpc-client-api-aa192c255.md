# Root-Cause Card

## Metadata

- ID: `reth-2025-09-25-reth-rpc-client-api-aa192c255`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-auth-header-parsing`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authentication-header-canonicalization`

## Violated Invariant

- Invariant: If this RPC layer accepts Bearer authentication, it should only extract a token when the Authorization header value begins with the exact "Bearer " scheme prefix. Accepting that marker from the middle of a larger string weakens the format check at the authentication boundary.

## Trust Boundary

- Boundary: http client -> authenticated rpc middleware

## Attack Surface

- Entrypoint type: rpc-auth-middleware
- Sensitive sink: jwt-protected rpc method access

## Impact Pattern

- Primary impact: auth-boundary-hardening
- Secondary impact: input-validation

## Short Reusable Lesson

- If this RPC layer accepts Bearer authentication, it should only extract a token when the Authorization header value begins with the exact "Bearer " scheme prefix. Accepting that marker from the middle of a larger string weakens the format check at the authentication boundary.
