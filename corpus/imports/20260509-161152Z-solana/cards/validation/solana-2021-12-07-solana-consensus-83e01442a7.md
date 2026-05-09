# Validation Card

## Metadata

- ID: `solana-2021-12-07-solana-consensus-83e01442a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rent-exemption-invariant-hardening`

## What Confirmed The Issue

- Commit subject names rejection of vote withdraws that create non-rent-exempt accounts.
- VoteInstruction::Withdraw now conditionally loads sysvar::rent under reject_non_rent_exempt_vote_withdraws.

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
