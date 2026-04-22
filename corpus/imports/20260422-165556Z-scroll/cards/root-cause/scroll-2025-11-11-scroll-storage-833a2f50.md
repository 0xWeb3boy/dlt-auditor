# Root-Cause Card

## Metadata

- ID: `scroll-2025-11-11-scroll-storage-833a2f50`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `key-material-handling`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `secret-handling-and-checked-length-validation`

## Violated Invariant

- Invariant: Proof metadata that contains decryption material should never be logged in plaintext, and unsafe FFI entrypoints must reject malformed key lengths with ordinary errors rather than panicking.

## Trust Boundary

- Boundary: `proof-metadata->ffi-boundary`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `native proof parsing and logging of validium key material`

## Impact Pattern

- Primary impact: `privileged-disclosure`
- Secondary impact: `denial-of-service`

## Short Reusable Lesson

- Proof metadata that contains decryption material should never be logged in plaintext, and unsafe FFI entrypoints must reject malformed key lengths with ordinary errors rather than panicking. The provided evidence supports a likely security-hardening change in the validium proof path. The patch removes logging of `chunkProof.MetaData.ChunkInfo.EncryptionKey` and replaces an `assert_eq!` on `decryption_key_len` in an `unsafe extern "C"` entrypoint with explicit validation and a failure return. The `codec_validium.go` schema change is adjacent protocol work, but the supplied evidence does not establish it as a proven vulnerability fix. The robust fix is to remove plaintext key-material logging and replace panic-based length assertions at the unsafe boundary with explicit validation and error returns.
