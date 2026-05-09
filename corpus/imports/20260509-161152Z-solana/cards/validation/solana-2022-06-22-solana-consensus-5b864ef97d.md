# Validation Card

## Metadata

- ID: `solana-2022-06-22-solana-consensus-5b864ef97d`
- Bug family: `resource_accounting_and_limits`
- Bug class: `quic-ingress-resource-limiting`

## What Confirmed The Issue

- Adds connection.set_max_concurrent_uni_streams for staked QUIC connections based on stake divided by total stake.
- Adds connection.set_max_concurrent_uni_streams for unstaked QUIC connections using QUIC_MAX_UNSTAKED_CONCURRENT_STREAMS.

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
