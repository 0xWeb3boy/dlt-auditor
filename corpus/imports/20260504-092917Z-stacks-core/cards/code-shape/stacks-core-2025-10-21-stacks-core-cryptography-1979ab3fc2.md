# Code-Shape Card

## Metadata

- ID: `stacks-core-2025-10-21-stacks-core-cryptography-1979ab3fc2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ambiguous-crypto-verification-api`

## Code Shape Summary

- The commit changes the secp256r1 verification API from returning Result<bool, &'static str> to returning Result<(), Secp256r1Error>. Invalid signatures now return Err(Secp256r1Error::InvalidSignature) instead of Ok(false), and tests were updated to match that contract. This is security-relevant crypto API hardening, but the evidence does not establish a concrete vulnerability or accepted invalid-signature path.

## Search Motifs

- Motif 1: signature verified without domain or chain context
- Motif 2: signer slot mapped to transaction origin only after acceptance
- Motif 3: block or vote accepted before reward-set membership is checked

## Typical Asymmetry

- The producer, peer, signer, or caller can choose fields that the consumer later treats as authoritative unless the missing property is checked at the boundary.

## Patch Pattern

- Derive the canonical signing context, reject malformed preimages, and verify signer identity before accepting or relaying the signed message.

## False Match Warnings

- A later consensus layer may repeat the full signature check.
- The code may only build test fixtures or diagnostics and never trust external messages.
