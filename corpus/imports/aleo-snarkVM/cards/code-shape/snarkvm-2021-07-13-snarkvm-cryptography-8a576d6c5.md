# Code-Shape Card

## Metadata

- ID: `snarkvm-2021-07-13-snarkvm-cryptography-8a576d6c5`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `signature-transcript-length-binding`

## Code Shape Summary

- A signature gadget built a Poseidon challenge from commitment field elements plus message field elements, but omitted an explicit byte length before absorbing the variable-length message.

## Search Motifs

- hash_input.extend(message.to_constraint_field(...)) without a nearby length or domain element
- signature gadget and native verifier construct challenge transcripts differently
- variable-length bytes are converted to field elements before a signature challenge hash

## Typical Asymmetry

- The code accepted or derived security-sensitive state before proving the boundary property named in the record: `transcript-boundary-binding`.

## Patch Pattern

- Insert an explicit message length or delimiter into the verifier transcript before absorbing encoded message field elements, and cover the verifier path with a regression test.

## False Match Warnings

- The message encoding is already canonical and length-delimited before it reaches the verifier.
- The changed code is test-only or does not feed an authorization or proof-validity decision.
- A separate transcript API already injects equivalent domain and length data.
