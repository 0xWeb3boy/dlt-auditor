# Validation Card

## Metadata

- ID: `scroll-2025-11-28-scroll-transaction-processing-752e4e11`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-fee-bounds`

## What Confirmed The Issue

- Evidence 1: In `rollup/internal/controller/sender/sender.go`, the patch replaces `blobBaseFee = misc.CalcBlobFee(*excess).Uint64()` with `// Leave it up to the L1 node to compute the correct blob base fee.`.
- Evidence 2: In `rollup/internal/controller/watcher/l1_watcher.go`, the patch replaces `blobBaseFee = misc.CalcBlobFee(*excess).Uint64()` with `// Leave it up to the L1 node to compute the correct blob base fee.`.
- Evidence 3: In `rollup/internal/controller/relayer/l1_relayer.go`, the patch replaces `data, err := r.l1GasOracleABI.Pack("setL1BaseFeeAndBlobBaseFee", new(big.Int).SetUint...` with `// Cap base fee update at the configured upper limit`.

## What Could Have Invalidated It

- Compensating control 1: If downstream contracts or nodes always clamp fee inputs to the same canonical bounds, a similar local fix may be mostly robustness work.
- Compensating control 2: Metric or logging changes around fees are not the core signal; the key issue is canonical fee sourcing plus upper bounds before relay.
- Compensating control 3: The evidence supports fee-path hardening, not a proven exploitable overflow.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If downstream contracts or nodes always clamp fee inputs to the same canonical bounds, a similar local fix may be mostly robustness work.
- Caution 2: Metric or logging changes around fees are not the core signal; the key issue is canonical fee sourcing plus upper bounds before relay.
- Caution 3: The evidence supports fee-path hardening, not a proven exploitable overflow.
