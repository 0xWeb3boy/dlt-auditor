# Validation Card

## Metadata

- ID: `solana-2020-11-19-solana-storage-a8c29505f0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `panic-dos`

## What Confirmed The Issue

- Commit body says over-the-wire pull requests can cause a validator panic through division by zero in bloom filters.
- runtime/src/bloom.rs changed Bloom<T> sanitization from an empty implementation to explicit validation.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: availability_or_resource_exhaustion
- Expected severity band: Medium
- Rationale: The impact primarily affects availability, liveness, or validator resource consumption rather than direct fund theft.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
