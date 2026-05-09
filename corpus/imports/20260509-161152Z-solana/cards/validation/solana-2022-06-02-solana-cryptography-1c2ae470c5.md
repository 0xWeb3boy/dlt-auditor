# Validation Card

## Metadata

- ID: `solana-2022-06-02-solana-cryptography-1c2ae470c5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `network-admission-control-hardening`

## What Confirmed The Issue

- `streamer/src/quic.rs` adds `if stake != 0 || max_unstaked_connections > 0` before adding and handling a QUIC connection.
- The commit body explicitly includes `no forwarding from unstaked nodes`, matching the added admission guard.

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
