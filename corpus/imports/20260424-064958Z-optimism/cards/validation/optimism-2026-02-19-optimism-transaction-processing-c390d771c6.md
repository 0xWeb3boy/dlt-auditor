# Validation Card

## Metadata

- ID: `optimism-2026-02-19-optimism-transaction-processing-c390d771c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- The commit body explicitly says zlib switched from unbounded decompression to a limit-aware API to prevent zip-bomb OOM.
- The Brotli implementation now caps initial/output buffer growth at max_rlp_bytes_per_channel and stops at the limit per spec.
- The changes sit in the batch/channel decompression path that processes protocol data before batch decoding.
- The patch adjusts runtime guards and failure handling around decompression size limits rather than only doing cleanup or refactoring.

## What Could Have Invalidated It

- The provided code excerpts do not show the exact zlib call replacement in the source diff.
- The patch alone does not establish which deployed roles or external actors can feed crafted channels to this path.
- No exploit demonstration or production impact data is provided beyond the commit description.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: availability-or-liveness
- Expected severity band: medium_or_low

## False-Positive Cautions

- The provided code excerpts do not show the exact zlib call replacement in the source diff.
- The patch alone does not establish which deployed roles or external actors can feed crafted channels to this path.
- No exploit demonstration or production impact data is provided beyond the commit description.
