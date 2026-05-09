# Validation Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-08bda35fd6`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Deploy/upgrade buffer verification now extracts authority_address instead of discarding it.
- The loader returns InstructionError::IncorrectAuthority when buffer authority does not match the upgrade authority under matching_buffer_upgrade_authorities.

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
- The account or authority is derived from trusted state and cannot be chosen by the caller.
