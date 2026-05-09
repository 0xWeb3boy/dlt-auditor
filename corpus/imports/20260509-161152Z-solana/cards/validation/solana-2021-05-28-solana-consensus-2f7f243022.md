# Validation Card

## Metadata

- ID: `solana-2021-05-28-solana-consensus-2f7f243022`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `read-only-account-modification-bypass`

## What Confirmed The Issue

- Commit subject says programs must always bail when modifying a read-only account.
- Deserialization no longer skips non-duplicate read-only accounts, allowing unauthorized mutations to be observed.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Medium
- Rationale: The issue was confirmed as a security fix, but the available evidence does not establish direct high-impact loss.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
