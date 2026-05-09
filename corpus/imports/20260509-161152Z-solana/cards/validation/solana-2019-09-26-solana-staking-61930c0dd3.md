# Validation Card

## Metadata

- ID: `solana-2019-09-26-solana-staking-61930c0dd3`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-check-hardening`

## What Confirmed The Issue

- Vote withdrawal now loads VoteState and verifies vote_state.authorized_withdrawer.
- Pre-patch withdrawal evidence only shows a generic vote_account signer requirement.

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
- The signature library or sanitized message type already commits the disputed field unconditionally.
