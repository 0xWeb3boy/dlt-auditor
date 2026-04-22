# Code-Shape Card

## Metadata

- ID: `scroll-2025-11-11-scroll-storage-833a2f50`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `key-material-handling`

## Code Shape Summary

- Short description of what the buggy code looked like: The provided evidence supports a likely security-hardening change in the validium proof path. The patch removes logging of `chunkProof.MetaData.ChunkInfo.EncryptionKey` and replaces an `assert_eq!` on `decryption_key_len` in an `unsafe extern "C"` entrypoint with explicit validation and a failure return. The `codec_validium.go` schema change is adjacent protocol work, but the supplied evidence does not establish it as a proven vulnerability fix.

## Search Motifs

- Motif 1: logging raw encryption or decryption keys from proof metadata
- Motif 2: assert_eq or panic-style length check inside unsafe extern or FFI entrypoint
- Motif 3: unsafe proof-decoding boundary converts malformed input into process abort instead of explicit error

## Typical Asymmetry

- What was checked in one path but missing in another: One path or representation enforced the canonical rule, identity, or compatibility gate while another parallel path, legacy branch, or helper-derived value reached the sink without the same binding.

## Patch Pattern

- What the fix changed structurally: Remove plaintext key-material logging and replace panic-based length assertions at the unsafe boundary with explicit validation and error returns.

## False Match Warnings

- Warning 1: If the logged key material is guaranteed synthetic test data and never present in production, a similar log line may be less significant.
- Warning 2: Defensive bounds checks elsewhere do not fully cure the issue when the unsafe entrypoint still panics on malformed lengths.
- Warning 3: The evidence supports strong hardening around secrets and FFI robustness, not a proven catastrophic exploit chain.
