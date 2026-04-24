# Root-Cause Card

## Metadata

- ID: `rippled-2014-02-18-rippled-cryptography-ae649ec91`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-canonicalization-hardening`
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

- Primary impact: transaction-malleability-reduction
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The supported finding is limited to ECDSA signature canonicalization hardening. The patch makes canonicality policy explicit in signature verification paths, most clearly in SerializedTransaction::checkSign, where tfFullyCanonicalSig selects ECDSA::strict and otherwise uses ECDSA::not_strict.
