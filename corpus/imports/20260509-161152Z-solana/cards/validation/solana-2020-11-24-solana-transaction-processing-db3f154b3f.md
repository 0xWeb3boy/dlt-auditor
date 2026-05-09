# Validation Card

## Metadata

- ID: `solana-2020-11-24-solana-transaction-processing-db3f154b3f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `durable-nonce-failed-transaction-state-persistence`

## What Confirmed The Issue

- Account persistence changed from all writable accounts to writable accounts gated by success or durable-nonce failure involving the nonce account or fee payer.
- The changed path is in runtime account collection after transaction processing, a state-update boundary.

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
