# Root-Cause Card

## Metadata

- ID: `reth-2025-09-25-reth-rpc-client-api-aa192c255`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-auth-header-parsing`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch tightens Bearer token parsing in `crates/rpc/rpc-layer/src/jwt_validator.rs`. Before, the helper accepted any Authorization header containing the substring `"Bearer "` anywhere; after, it requires the header to start with that prefix. The evidence shows a malformed header was previously treated as a Bearer token source, but it does not establish a concrete authentication bypass or broader exploit from that behavior alone.
