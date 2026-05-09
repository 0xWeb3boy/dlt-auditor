# Code-Shape Card

## Metadata

- ID: `solana-2021-06-06-solana-transaction-processing-e5ea16fad8`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-check-bypass`

## Code Shape Summary

The supported finding is limited to an authorization check gap in zero-lamport System Program transfers. Before the patch, `transfer` returned `Ok(())` for `lamports == 0` before checking whether the source account signed. After the patch, that legacy early return is gated behind `!system_transfer_zero_check`, so when the feature is active the existing missing-signature check runs and unsigned zero-lamport transfers fail.

## Search Motifs

- search for authorization check bypass checks near transaction-processing entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Gate or remove special-case zero-value fast paths so authorization checks still execute before success is returned.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
