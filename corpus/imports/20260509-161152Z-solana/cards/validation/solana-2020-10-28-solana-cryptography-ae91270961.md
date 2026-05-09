# Validation Card

## Metadata

- ID: `solana-2020-10-28-solana-cryptography-ae91270961`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-amplification-via-source-spoofing`

## What Confirmed The Issue

- Commit body cites a HackerOne report describing UDP gossip amplification via spoofed PullRequest source addresses.
- Patch introduces Ping/Pong protocol message handling with verification before accepting those messages.

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
