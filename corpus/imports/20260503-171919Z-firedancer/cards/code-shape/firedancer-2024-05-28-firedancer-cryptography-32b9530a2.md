# Code-Shape Card

## Metadata

- ID: `firedancer-2024-05-28-firedancer-cryptography-32b9530a2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `retry-token-forgery`

## Code Shape Summary

- Retry token encryption and decryption lacked per-instance secret binding, so token acceptance depended on predictable structure rather than server-held authenticity material.

## Search Motifs

- Motif 1: retry token encrypt/decrypt missing server secret
- Motif 2: stateless token accepted without instance-specific key
- Motif 3: anti-abuse token derived only from public packet data

## Typical Asymmetry

- The peer can present arbitrary token bytes, but only the server should be able to mint an acceptable token.

## Patch Pattern

- Introduce a per-instance secret at initialization and thread it through every token encryption and validation call.

## False Match Warnings

- No full exploit trace or proof-of-concept is provided.
- No evidence shows which deployments or configurations enabled Retry tokens.
