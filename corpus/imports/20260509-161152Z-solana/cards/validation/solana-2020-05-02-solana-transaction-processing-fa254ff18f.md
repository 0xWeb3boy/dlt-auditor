# Validation Card

## Metadata

- ID: `solana-2020-05-02-solana-transaction-processing-fa254ff18f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-transaction-validation-ordering`

## What Confirmed The Issue

- `Accounts::lock_accounts` now calls `tx.sanitize()` before deriving account lock keys.
- Duplicate account keys are rejected in `lock_accounts` before lock acquisition logic proceeds.

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
