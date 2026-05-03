# Code-Shape Card

## Metadata

- ID: `firedancer-2024-11-27-firedancer-storage-2bc30f00b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `crypto-precompile-input-validation-hardening`

## Code Shape Summary

- The precompile path decoded secp256r1 scalars and compressed keys with weaker format discipline than the verifier contract expected.

## Search Motifs

- Motif 1: scalar byte copy fixed in precompile parser
- Motif 2: compressed key y-coordinate handling corrected
- Motif 3: cryptographic deserializer tightened before verify call

## Typical Asymmetry

- The attacker controls cryptographic input shape, but the verifier relies on helper routines to normalize it before the real check.

## Patch Pattern

- Validate scalar widths and point encodings up front, then feed only normalized values into the cryptographic verifier.

## False Match Warnings

- No end-to-end transaction or exploit proof shows that invalid signatures were accepted before the patch.
- No demonstrated consensus divergence, funds-at-risk, privilege bypass, or authentication bypass is provided.
