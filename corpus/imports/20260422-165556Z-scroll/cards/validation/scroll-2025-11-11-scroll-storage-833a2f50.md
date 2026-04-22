# Validation Card

## Metadata

- ID: `scroll-2025-11-11-scroll-storage-833a2f50`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `key-material-handling`

## What Confirmed The Issue

- Evidence 1: In `crates/libzkp_c/src/lib.rs`, the patch replaces `assert_eq!(decryption_key_len, 32, "len(decryption_key) != 32");` with `if decryption_key_len != 32 {`.
- Evidence 2: In `coordinator/internal/utils/codec_validium.go`, the patch replaces `Version CodecVersion 'json:"version"'` with `Version CodecVersion 'json:"version"'`.
- Evidence 3: In `coordinator/internal/logic/submitproof/proof_receiver.go`, the patch removes `log.Info("parse chunkproof", "key", chunkProof.MetaData.ChunkInfo.EncryptionKey)`.

## What Could Have Invalidated It

- Compensating control 1: If the logged key material is guaranteed synthetic test data and never present in production, a similar log line may be less significant.
- Compensating control 2: Defensive bounds checks elsewhere do not fully cure the issue when the unsafe entrypoint still panics on malformed lengths.
- Compensating control 3: The evidence supports strong hardening around secrets and FFI robustness, not a proven catastrophic exploit chain.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: If the logged key material is guaranteed synthetic test data and never present in production, a similar log line may be less significant.
- Caution 2: Defensive bounds checks elsewhere do not fully cure the issue when the unsafe entrypoint still panics on malformed lengths.
- Caution 3: The evidence supports strong hardening around secrets and FFI robustness, not a proven catastrophic exploit chain.
