# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-11-13-oasis-core-rpc-client-api-75e2e189e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-on-malformed-input`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Public keys used as identities must decode to exactly 'PublicKeySize' bytes, and malformed keys must be rejected or handled as invalid values without panicking during later map-key conversion or registry validation.

## Trust Boundary

- Boundary: `remote-peer->rpc-verifier`

## Attack Surface

- Entrypoint type: `rpc-handler`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `none`

## Short Reusable Lesson

- Public keys used as identities must decode to exactly 'PublicKeySize' bytes, and malformed keys must be rejected or handled as invalid values without panicking during later map-key conversion or registry validation. In this pattern, malformed public keys were handled inconsistently across the code path: deserialization allowed a nil/zero-length key as success, but later identity-conversion logic assumed exact key length and could panic when given that malformed value. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
