# Root-Cause Card

## Metadata

- ID: `sui-2022-07-29-sui-cryptography-24d683b660`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-malleability`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `signature-canonicalization`

## Violated Invariant

- Invariant: A verifier must accept only the canonical signed representation that was bound to the intended signer, domain, and message semantics.

## Trust Boundary

- Boundary: signed payload or certificate bytes -> trust decision

## Attack Surface

- Entrypoint type: signature-verification-path
- Sensitive sink: accepting a signature, certificate, or signed digest as authoritative

## Impact Pattern

- Primary impact: signature-malleability
- Secondary impact: context-dependent

## Short Reusable Lesson

- Signature checks are only useful when they bind the exact signer set, message bytes, domain, and epoch consumed by the privileged path. The patch fixes secp256k1 recoverable signature malleability in `narwhal/crypto/src/secp256k1.rs`. The old verifier converted the recoverable signature to a standard ECDSA signature with `to_standard()` and verified that value against the public key.
