# Validation Card

## Metadata

- ID: `solana-2020-10-28-solana-cryptography-f19778b7d9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-reflection-amplification`

## What Confirmed The Issue

- Commit body explicitly cites spoofed UDP PullRequest amplification and DDoS risk.
- Patch adds PingMessage and PongMessage verification to gossip protocol handling.

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
