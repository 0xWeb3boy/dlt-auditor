# Validation Card

## Metadata

- ID: `snarkvm-2021-11-11-snarkvm-cryptography-93e7c65a8`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `cryptographic-domain-separation-hardening`

## What Confirmed The Issue

- The ECIES Poseidon gadget now absorbs `AleoEncryption2021` with derived key material.
- Record commitment randomness derivation was made explicit from the record view key.

## What Could Have Invalidated It

- A surrounding transcript layer already injected the same domain separator.
- The changed derivation output is never consumed by verification or state logic.

## Severity Guidance

- Expected impact band: cryptographic_binding_hardening
- Expected severity band: medium_or_low

## False-Positive Cautions

- The caller already includes an unambiguous domain tag in the absorbed data.
- The derivation is private to one fixed scheme with no reusable output domain.
