# Validation Card

## Metadata

- ID: `solana-2020-11-20-solana-storage-ff38a46af6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `remote-denial-of-service`

## What Confirmed The Issue

- Commit message identifies over-the-wire pull requests as the source of malformed input.
- Commit message names validator panic due to division by zero in bloom filters.

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
