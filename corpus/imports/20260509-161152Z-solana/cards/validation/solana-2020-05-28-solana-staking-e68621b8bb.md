# Validation Card

## Metadata

- ID: `solana-2020-05-28-solana-staking-e68621b8bb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `denial-of-service`

## What Confirmed The Issue

- Commit subject is "Fix repair dos (#10299)".
- Runtime behavior changes from ignoring a failed packet construction to breaking orphan traversal on None.

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
