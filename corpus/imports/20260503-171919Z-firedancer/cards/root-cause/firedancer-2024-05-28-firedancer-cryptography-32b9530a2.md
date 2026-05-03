# Root-Cause Card

## Metadata

- ID: `firedancer-2024-05-28-firedancer-cryptography-32b9530a2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `retry-token-forgery`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `server-secret-token-authentication`

## Violated Invariant

- Invariant: Stateless retry tokens must be cryptographically bound to a server secret so clients cannot mint acceptable tokens offline.

## Trust Boundary

- Boundary: Unauthenticated client token material crossing into server retry-token validation.

## Attack Surface

- Entrypoint type: handshake token validation
- Sensitive sink: acceptance of Retry-protected connection state

## Impact Pattern

- Primary impact: address validation bypass
- Secondary impact: token spoofing

## Short Reusable Lesson

- Retry token encryption and decryption lacked per-instance secret binding, so token acceptance depended on predictable structure rather than server-held authenticity material.
