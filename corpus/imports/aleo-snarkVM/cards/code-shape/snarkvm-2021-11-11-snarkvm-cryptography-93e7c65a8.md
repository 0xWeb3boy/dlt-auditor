# Code-Shape Card

## Metadata

- ID: `snarkvm-2021-11-11-snarkvm-cryptography-93e7c65a8`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cryptographic-domain-separation-hardening`

## Code Shape Summary

- ECIES Poseidon gadget paths absorbed bare ECDH or symmetric-key coordinate material before squeezing derived values, without a visible scheme domain separator.

## Search Motifs

- Poseidon sponge absorbs only key coordinates before deriving commitments
- encryption gadget lacks a constant protocol label
- record commitment randomness derived implicitly from view-key material

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `domain-separation`.

## Patch Pattern

- Absorb a constant scheme label with the key material and make record commitment randomness derivation explicit.

## False Match Warnings

- The caller already includes an unambiguous domain tag in the absorbed data.
- The derivation is private to one fixed scheme with no reusable output domain.
- Only comments or tests changed, with no sponge input change.
