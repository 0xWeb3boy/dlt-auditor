# Validation Card

## Metadata

- ID: `movement-2025-01-21-movement-cryptography-39db1ab68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- InnerSignedBlobV1Data::try_new rejects blob.len() greater than MAX_BLOB_LEN.
- try_verify checks signature length before ECDSA parsing.
- A regression test covers wrong-length signatures not panicking.

## What Could Have Invalidated It

- All blob bytes are already size-bounded before reaching this constructor.
- The malformed signature path already returned a recoverable error on all supported curves.
- The changed code is only test-only or unreachable from untrusted inputs.

## Severity Guidance

- Expected impact band: availability_hardening
- Expected severity band: medium_or_low
- Rationale: The patch targets resource-control and panic avoidance in DA cryptographic parsing, but the raw evidence does not prove a remotely exploitable zstd bomb or crash.

## False-Positive Cautions

- Do not claim zstd decompression exploit unless decompression code or expansion path is shown.
- Do not classify as authentication bypass from a signature-length guard alone.
