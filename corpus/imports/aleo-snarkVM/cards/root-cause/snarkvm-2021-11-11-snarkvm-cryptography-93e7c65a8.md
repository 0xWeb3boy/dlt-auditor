# Root-Cause Card

## Metadata

- ID: `snarkvm-2021-11-11-snarkvm-cryptography-93e7c65a8`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cryptographic-domain-separation-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `domain-separation`

## Violated Invariant

- Invariant: Cryptographic sponge inputs used for encryption, commitments, or proofs must include scheme-specific context so derived values cannot be confused across domains.

## Trust Boundary

- Boundary: protocol key material -> cryptographic sponge derivation

## Attack Surface

- Entrypoint type: cryptographic-derivation-path
- Sensitive sink: Poseidon-derived encryption and commitment randomness

## Impact Pattern

- Primary impact: cryptographic binding hardening
- Secondary impact: reduced risk of cross-context derivation confusion

## Short Reusable Lesson

- Reusable cryptographic primitives should be wrapped with protocol labels at every derivation boundary, especially inside gadgets that mirror native logic.
