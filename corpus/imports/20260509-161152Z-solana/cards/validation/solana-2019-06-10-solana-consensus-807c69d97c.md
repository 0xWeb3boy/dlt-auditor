# Validation Card

## Metadata

- ID: `solana-2019-06-10-solana-consensus-807c69d97c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-permission-invariant-hardening`

## What Confirmed The Issue

- verify_instruction now rejects lamport decreases when is_debitable is false via CreditOnlyLamportSpend.
- verify_instruction now rejects data changes when is_debitable is false via CreditOnlyDataModified.

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
- The account or authority is derived from trusted state and cannot be chosen by the caller.
