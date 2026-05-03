# Code-Shape Card

## Metadata

- ID: `movement-2024-11-20-movement-cryptography-3f265410b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signed-field-not-bound`

## Code Shape Summary

- The signature digest for a DA signed blob covered inner blob data and timestamp but not the wrapper id. The fix signs and verifies a digest that includes blob, timestamp, and id, binding the wrapper identity to the signature.

## Search Motifs

- verify wrapper by delegating to self.data.try_verify without wrapper fields
- signature digest omits id, namespace, chain id, height, or domain field
- patch adds wrapper field to hash before ECDSA verification
- tests or constructors distinguish inner data from signed envelope metadata

## Typical Asymmetry

- The signed inner payload looked authenticated, while wrapper metadata still influenced identity outside the digest.

## Patch Pattern

- Build the signed digest at the envelope layer and include all security-relevant wrapper fields before signature generation and verification.

## False Match Warnings

- Do not flag omitted fields that are purely cached or recomputable and never influence trust decisions.
- Do not claim forgery if the omitted field is independently authenticated elsewhere.
- Formatting-only verifier hunks are not evidence of a cryptographic bug.
