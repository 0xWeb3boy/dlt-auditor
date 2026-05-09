# Validation Card

## Metadata

- ID: `solana-2023-01-31-solana-cryptography-a5af54669a`
- Bug family: `resource_accounting_and_limits`
- Bug class: `missing-resource-limit`

## What Confirmed The Issue

- Adds feature-gated requested loaded account data size limit of 64 MiB.
- Accumulates each loaded account's data length during transaction account loading.

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
