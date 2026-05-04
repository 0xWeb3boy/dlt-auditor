# Validation Card

## Metadata

- ID: `snarkvm-2021-07-13-snarkvm-cryptography-8a576d6c5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-transcript-length-binding`

## What Confirmed The Issue

- The implementation adds `message.len()` to the GroupEncryption gadget hash input.
- A GroupEncryption gadget signature verification test was added with the patch.

## What Could Have Invalidated It

- Native and circuit verification already shared a length-delimited transcript outside the shown hunk.
- The message being verified is fixed-size by construction at all call sites.

## Severity Guidance

- Expected impact band: cryptographic_integrity_hardening
- Expected severity band: medium_or_low

## False-Positive Cautions

- The message encoding is already canonical and length-delimited before it reaches the verifier.
- The changed code is test-only or does not feed an authorization or proof-validity decision.
