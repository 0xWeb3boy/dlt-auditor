# Validation Card

## Metadata

- ID: `solana-2020-11-16-solana-staking-e12cb457fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-owner-validation`

## What Confirmed The Issue

- Adds a vote account owner check requiring `solana_vote_program::id()` before delegation logic proceeds.
- Adds stake program owner checks for split and merge account inputs before state handling proceeds.

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
- The account or authority is derived from trusted state and cannot be chosen by the caller.
