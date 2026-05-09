# Validation Card

## Metadata

- ID: `solana-2021-12-06-solana-consensus-e123883b26`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-rent-exemption-check`

## What Confirmed The Issue

- Commit subject states vote withdraws creating non-rent-exempt accounts are rejected.
- Withdraw processing now fetches Rent sysvar under the reject_non_rent_exempt_vote_withdraws feature gate.

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
