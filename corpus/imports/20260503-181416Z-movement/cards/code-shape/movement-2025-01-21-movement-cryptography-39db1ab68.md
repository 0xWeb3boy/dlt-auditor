# Code-Shape Card

## Metadata

- ID: `movement-2025-01-21-movement-cryptography-39db1ab68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## Code Shape Summary

- A signed DA blob data constructor became fallible and rejects blobs above MAX_BLOB_LEN. The verifier also checks signature length before ECDSA parsing, with a regression test ensuring wrong-length signatures return errors instead of panicking.

## Search Motifs

- constructor new(blob: Vec<u8>) stores unbounded bytes
- patch renames new to try_new and returns Result on oversized input
- ECDSA Signature::from_bytes called before checking signature.len
- regression test named does_not_panic_on_wrong_signature_len

## Typical Asymmetry

- Parsing and construction accepted untrusted byte vectors before enforcing the size and fixed-width assumptions used later.

## Patch Pattern

- Make blob construction fallible with an explicit maximum length, propagate constructor errors, and reject malformed fixed-size signatures before cryptographic parser conversion.

## False Match Warnings

- Do not claim zstd decompression exploit unless decompression code or expansion path is shown.
- Do not classify as authentication bypass from a signature-length guard alone.
- If MAX_BLOB_LEN is enforced earlier on every external path, this constructor change may be defense in depth.
