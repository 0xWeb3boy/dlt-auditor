# Validation Card

## Metadata

- ID: `solana-2023-05-25-solana-transaction-processing-9d6c921b5f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `underconstrained-transaction-classification`

## What Confirmed The Issue

- SanitizedTransaction::try_create now requires signatures.len() < 3 before deriving is_simple_vote_tx.
- The commit subject states simple votes should have 1 or 2 signatures during sanitized transaction creation.

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
- The signature library or sanitized message type already commits the disputed field unconditionally.
