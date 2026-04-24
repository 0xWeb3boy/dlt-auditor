# Validation Card

## Metadata

- ID: `optimism-2026-03-26-optimism-transaction-processing-b08e543ddf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`

## What Confirmed The Issue

- Brotli decompression now caps the initial output buffer at max_rlp_bytes_per_channel to avoid over-allocation.
- The decompression loop is changed to stop at the configured cap instead of continuing growth past the limit.
- New tests explicitly validate truncation-at-limit behavior rather than rejection, showing deliberate resource-bound enforcement.
- The affected code is in batch/channel derivation logic that processes compressed protocol input, making the resource bound security-relevant.

## What Could Have Invalidated It

- No supplied diff excerpt shows the claimed zlib limit change or the exact pre-patch unbounded zlib call.
- No evidence demonstrates an actual crash, OOM, or remotely triggerable exploit in deployed nodes.
- The excerpts do not show attack reachability, privileges required, or real-world impact beyond hardening/resource control.
- an earlier boundary already rejects the same malformed field under all reachable modes

## Severity Guidance

- Expected impact band: availability-or-liveness
- Expected severity band: medium_or_low

## False-Positive Cautions

- No supplied diff excerpt shows the claimed zlib limit change or the exact pre-patch unbounded zlib call.
- No evidence demonstrates an actual crash, OOM, or remotely triggerable exploit in deployed nodes.
- The excerpts do not show attack reachability, privileges required, or real-world impact beyond hardening/resource control.
