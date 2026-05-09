# Validation Card

## Metadata

- ID: `solana-2019-12-20-solana-cryptography-3c361eb759`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `snapshot-integrity-validation`

## What Confirmed The Issue

- verify_bank_hash now recomputes each non-sysvar account hash with Self::hash_account(slot, &account, pubkey).
- The verifier compares the recomputed hash against account.hash and records mismatch_found on disagreement.

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
