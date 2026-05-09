# Validation Card

## Metadata

- ID: `solana-2020-10-29-solana-cryptography-06067dd823`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `udp-amplification-missing-endpoint-validation`

## What Confirmed The Issue

- Commit message explicitly describes spoofed UDP PullRequest source addresses causing larger PullResponse traffic to a victim.
- Patch adds check_pull_request requiring a valid address and prior ping response before accepting pull requests for response generation.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: availability_or_resource_exhaustion
- Expected severity band: Medium
- Rationale: The issue was confirmed as a security fix, but the available evidence does not establish direct high-impact loss.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
