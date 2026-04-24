# Validation Card

## Metadata

- ID: `reth-2024-09-02-reth-consensus-d59854f1d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-runtime-bound-check`

## What Confirmed The Issue

- TreeState::remove_until previously relied on debug_assert!(Some(upper_bound) >= finalized_num), which is not enforced in release builds.
- The patch now clamps the input with finalized.min(upper_bound) before continuing removal logic.

## What Could Have Invalidated It

- No evidence shows that untrusted peers or external inputs can force finalized_num > upper_bound
- No reproducer or test demonstrates harmful pre-patch behavior in release builds

## Severity Guidance

- Expected impact band: consensus_or_protocol_integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- No evidence shows that untrusted peers or external inputs can force finalized_num > upper_bound
- No reproducer or test demonstrates harmful pre-patch behavior in release builds
