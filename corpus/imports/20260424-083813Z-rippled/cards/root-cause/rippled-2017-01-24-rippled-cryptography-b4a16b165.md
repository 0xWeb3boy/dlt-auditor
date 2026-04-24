# Root-Cause Card

## Metadata

- ID: `rippled-2017-01-24-rippled-cryptography-b4a16b165`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-key-revocation-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signer-scope-and-domain-binding`

## Violated Invariant

- Invariant: Signed or hashed protocol objects must bind the intended signer, object type, domain, and revocation state before the object is trusted.

## Trust Boundary

- Boundary: signed object or key material -> local trust and verification decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: accepted signature, signer identity, manifest, or replay-sensitive object

## Impact Pattern

- Primary impact: compromised-key-containment, validator-trust-management
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch adds first-class handling for validator master-key revocation manifests and a dedicated [validator_key_revocation] config input.
