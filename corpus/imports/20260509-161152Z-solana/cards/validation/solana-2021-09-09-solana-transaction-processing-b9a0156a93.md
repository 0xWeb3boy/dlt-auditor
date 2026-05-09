# Validation Card

## Metadata

- ID: `solana-2021-09-09-solana-transaction-processing-b9a0156a93`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-writable-account-validation`

## What Confirmed The Issue

- Commit message explicitly says transactions should error when containing writable executable or ProgramData accounts.
- Runtime account loading now checks upgradeable-loader ownership rather than only executable upgradeable-loader accounts.

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
