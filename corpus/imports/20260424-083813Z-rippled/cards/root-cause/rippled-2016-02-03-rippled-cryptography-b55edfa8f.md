# Root-Cause Card

## Metadata

- ID: `rippled-2016-02-03-rippled-cryptography-b55edfa8f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `validator-manifest-signature-hardening`
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

- Primary impact: cryptographic-integrity
- Secondary impact: Protocol-local correctness or hardening impact bounded by the reachable subsystem and surrounding checks.

## Short Reusable Lesson

- The patch changes validator manifest signing and verification from an observed single master-key verification path to a dual-signature manifest format involving both validation key material and master key material.
