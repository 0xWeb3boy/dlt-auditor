# Validation Card

## Metadata

- ID: `solana-2021-05-28-solana-consensus-a3240aebde`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `read-only-account-mutation`

## What Confirmed The Issue

- Commit subject says the fix is to always bail if a program modifies a read-only account.
- Runtime account lookup now prefers pre-instruction account state before account dependencies.

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
- The account or authority is derived from trusted state and cannot be chosen by the caller.
