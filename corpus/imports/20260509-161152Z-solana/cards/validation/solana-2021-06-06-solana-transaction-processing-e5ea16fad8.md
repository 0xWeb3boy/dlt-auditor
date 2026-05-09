# Validation Card

## Metadata

- ID: `solana-2021-06-06-solana-transaction-processing-e5ea16fad8`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-check-bypass`

## What Confirmed The Issue

- The transfer handler changed an unconditional `lamports == 0` early return into a feature-gated legacy path.
- The shown post-patch control flow reaches `from.signer_key().is_none()` when `system_transfer_zero_check` is active.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: defense_in_depth_or_input_hardening
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
