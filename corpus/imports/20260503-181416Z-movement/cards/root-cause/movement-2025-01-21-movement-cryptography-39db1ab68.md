# Root-Cause Card

## Metadata

- ID: `movement-2025-01-21-movement-cryptography-39db1ab68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `decoded-blob-size-and-signature-length-validation`

## Violated Invariant

- Invariant: Untrusted encoded or decoded DA blob data must be size-bounded before acceptance, and fixed-width cryptographic encodings must be length-checked before parser conversion.

## Trust Boundary

- Boundary: Celestia DA blob and signature bytes crossing from network/storage input into signed blob verification.

## Attack Surface

- Entrypoint type: DA blob deserialization and signature verification
- Sensitive sink: allocation, decompression-adjacent blob representation, and ECDSA signature parsing

## Impact Pattern

- Primary impact: Resource exhaustion or panic from malformed DA blob inputs.
- Secondary impact: More robust cryptographic verifier error handling.

## Short Reusable Lesson

- A signed DA blob data constructor became fallible and rejects blobs above MAX_BLOB_LEN. The verifier also checks signature length before ECDSA parsing, with a regression test ensuring wrong-length signatures return errors instead of panicking. Make blob construction fallible with an explicit maximum length, propagate constructor errors, and reject malformed fixed-size signatures before cryptographic parser conversion.
