# Code-Shape Card

## Metadata

- ID: `solana-2021-06-07-solana-transaction-processing-b777bbf7db`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authorization-check`

## Code Shape Summary

The supported finding is limited to authorization hardening in Solana's runtime system-program transfer path. Before the patch, `transfer` returned `Ok(())` immediately for `lamports == 0`, before checking whether the source account signed. After the patch, that early return is feature-gated, so once `system_transfer_zero_check` is active, zero-lamport transfers enter the normal signer-validation path and unsigned transfers fail with `InstructionError::...

## Search Motifs

- search for missing authorization check checks near transaction-processing entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Gate or remove zero-value fast paths that bypass authorization so no-op amounts still pass through the same signature validation required for the instruction type.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
