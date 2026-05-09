# Validation Card

## Metadata

- ID: `solana-2019-09-12-solana-staking-5dceeec1ca`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization`

## What Confirmed The Issue

- Sensitive staking operations changed from `self.signer_key().is_none()` checks to explicit state-derived authorization checks.
- `delegate_stake` now calls `lockup.check_authorized(...)` before creating delegated stake state.

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
