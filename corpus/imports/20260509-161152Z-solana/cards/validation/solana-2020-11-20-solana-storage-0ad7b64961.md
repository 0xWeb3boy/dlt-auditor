# Validation Card

## Metadata

- ID: `solana-2020-11-20-solana-storage-0ad7b64961`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-input-validation`

## What Confirmed The Issue

- Commit body states pull requests received over the wire can cause a validator panic via division by zero in Bloom filters.
- Bloom<T> previously had a no-op Sanitize implementation.

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
