# Validation Card

## Metadata

- ID: `solana-2020-05-02-solana-cryptography-f37f83fd12`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sanitization-ordering`

## What Confirmed The Issue

- `lock_accounts` now calls `tx.sanitize()` before deriving account lock keys.
- Duplicate account keys are rejected in `lock_accounts` with `TransactionError::AccountLoadedTwice`.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: Low/Medium
- Rationale: The finding is useful security-hardening evidence; severity depends on reachability and missing compensating controls.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
