# Validation Card

## Metadata

- ID: `solana-2021-09-09-solana-transaction-processing-3eee222667`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-writable-account-validation`

## What Confirmed The Issue

- Commit message explicitly says transactions with writable executable or ProgramData accounts should return an error.
- runtime/src/accounts.rs broadens validation from executable upgradeable-loader-owned accounts to all upgradeable-loader-owned accounts.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: state_integrity_or_policy_bypass
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
