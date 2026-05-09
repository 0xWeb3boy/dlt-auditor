# Validation Card

## Metadata

- ID: `solana-2019-09-25-solana-staking-43795193c4`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-hardening`

## What Confirmed The Issue

- `withdraw` now loads `VoteState` and calls `verify_authorized_signer` against `vote_state.authorized_withdrawer`.
- The previous shown withdrawal gate only checked `vote_account.signer_key().is_none()`, which is a generic signer requirement rather than a role-specific authority check.

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
