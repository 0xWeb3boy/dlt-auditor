# Validation Card

## Metadata

- ID: `solana-2023-02-01-solana-cryptography-8270f29b0c`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit`

## What Confirmed The Issue

- Adds a transaction-level cap for loaded account data when the feature gate is active.
- Checks accumulated loaded account data size inside the runtime account-loading path.

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
