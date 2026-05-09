# Validation Card

## Metadata

- ID: `solana-2021-06-01-solana-cryptography-b000d490ce`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion-mitigation`

## What Confirmed The Issue

- Adds CostModel and CostTracker to the banking-stage transaction conversion path.
- Calculates transaction cost before admitting transactions for processing.

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
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
