# Validation Card

## Metadata

- ID: `solana-2022-06-02-solana-cryptography-a781cff386`
- Bug family: `staking_registry_and_accountability`
- Bug class: `quic-stake-admission-control`

## What Confirmed The Issue

- QUIC connection handling is newly guarded by stake != 0 || max_unstaked_connections > 0.
- The guarded path includes try_add_connection and handle_connection for remote QUIC peers.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: Medium
- Rationale: The impact primarily affects availability, liveness, or validator resource consumption rather than direct fund theft.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The expensive allocation is bounded by a separately enforced stake, peer, or per-request quota.
