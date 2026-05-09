# Validation Card

## Metadata

- ID: `solana-2022-09-22-solana-transaction-processing-565aacc23a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-account-mutability-check`

## What Confirmed The Issue

- Runtime code adds a borrow of PROGRAM_ACCOUNT_INDEX before continuing the extend operation.
- Runtime code rejects the instruction when program_account.is_writable() is false.

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
