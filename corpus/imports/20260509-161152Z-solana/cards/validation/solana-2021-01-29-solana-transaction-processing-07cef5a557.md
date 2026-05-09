# Validation Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-07cef5a557`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-enforcement`

## What Confirmed The Issue

- Deploy/upgrade buffer validation now reads authority_address and rejects when it differs from the supplied authority under matching_buffer_upgrade_authorities.
- The SetAuthority path rejects clearing buffer authority to None while the same feature is active, preserving the enforceable authority invariant.

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
