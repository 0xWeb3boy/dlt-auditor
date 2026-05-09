# Validation Card

## Metadata

- ID: `solana-2020-07-21-solana-staking-e07c00710a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reward-accounting-invariant`

## What Confirmed The Issue

- Patch adds a post-payment assertion that validator rewards paid do not exceed allocated validator rewards.
- Patch checks observed paid rewards against the recorded rewards sum when rewards records exist.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
