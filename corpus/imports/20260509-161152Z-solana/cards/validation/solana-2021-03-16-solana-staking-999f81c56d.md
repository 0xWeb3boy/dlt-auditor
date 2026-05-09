# Validation Card

## Metadata

- ID: `solana-2021-03-16-solana-staking-999f81c56d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-resource-metering`

## What Confirmed The Issue

- Registers a new cpi_data_cost feature described as charging compute budget for data passed via CPI.
- Adds compute-meter consumption based on CPI account data length in the Rust AccountInfo translation path.

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
