# Validation Card

## Metadata

- ID: `solana-2022-06-03-solana-transaction-processing-5ee157f43d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `replay-domain-collision`

## What Confirmed The Issue

- Commit body states durable nonce and blockhash shared a domain could permit double execution.
- Commit body states the fix separates nonce and blockhash domains by hashing blockhash with a fixed string.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: Medium
- Rationale: The issue was confirmed as a security fix, but the available evidence does not establish direct high-impact loss.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
