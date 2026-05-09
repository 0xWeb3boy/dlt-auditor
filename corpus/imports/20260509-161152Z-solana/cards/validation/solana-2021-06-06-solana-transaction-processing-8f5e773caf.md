# Validation Card

## Metadata

- ID: `solana-2021-06-06-solana-transaction-processing-8f5e773caf`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authorization`

## What Confirmed The Issue

- `transfer` changed the unconditional `lamports == 0` early `Ok(())` return into a feature-gated legacy branch.
- With `system_transfer_zero_check` active, zero-lamport transfers proceed to `from.signer_key().is_none()` validation.

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
