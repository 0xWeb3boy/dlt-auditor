# Validation Card

## Metadata

- ID: `solana-2021-12-07-solana-consensus-89d2f34a03`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-invariant-enforcement`

## What Confirmed The Issue

- Commit subject says vote withdraws creating non-rent-exempt accounts are rejected.
- Vote withdraw processing conditionally loads the Rent sysvar when reject_non_rent_exempt_vote_withdraws is active.

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
