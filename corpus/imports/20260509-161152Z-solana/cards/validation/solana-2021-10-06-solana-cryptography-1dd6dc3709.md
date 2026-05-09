# Validation Card

## Metadata

- ID: `solana-2021-10-06-solana-cryptography-1dd6dc3709`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-accounting-hardening`

## What Confirmed The Issue

- Commit body says the cost model limits transactions that are not parallelizeable.
- Commit body describes a fixed-capacity ExecuteCostTable added for a security concern.

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
