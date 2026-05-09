# Code-Shape Card

## Metadata

- ID: `solana-2021-06-06-solana-transaction-processing-8f5e773caf`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authorization`

## Code Shape Summary

The grounded security-relevant change is in the system-program transfer handler. Previously, `transfer` returned `Ok(())` immediately for `lamports == 0`, before checking whether the source account had signed. The patch feature-gates that legacy fast path so that, once `system_transfer_zero_check` is active, zero-lamport transfers continue to the existing missing-signature check. This supports a missing-authorization hardening finding, but the evidence...

## Search Motifs

- search for missing authorization checks near transaction-processing entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Do not let no-op or zero-value fast paths bypass authorization checks. Gate legacy behavior where needed and route active behavior through the same validation path as normal state-changing operations.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
