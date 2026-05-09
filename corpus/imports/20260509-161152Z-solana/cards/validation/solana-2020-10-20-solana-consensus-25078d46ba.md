# Validation Card

## Metadata

- ID: `solana-2020-10-20-solana-consensus-25078d46ba`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `gossip-stale-peer-fanout`

## What Confirmed The Issue

- Commit body references a DDOS issue involving nodes that go offline and redundant duplicate push traffic.
- `push_options` now computes an active cutoff from the current timestamp and `PUSH_ACTIVE_TIMEOUT_MS`.

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
