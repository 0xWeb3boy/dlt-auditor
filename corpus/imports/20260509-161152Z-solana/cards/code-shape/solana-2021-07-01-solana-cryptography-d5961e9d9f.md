# Code-Shape Card

## Metadata

- ID: `solana-2021-07-01-solana-cryptography-d5961e9d9f`
- Bug family: `signature_binding_and_signer_scope`
- Bug class: `transaction-signature-length-validation`

## Code Shape Summary

The patch adds explicit `verify_signatures_len()` checks in RPC transaction verification and ledger entry transaction verification, and adds RPC error plumbing for signature length mismatch. The evidence supports a transaction validation/canonicality tightening for extra or mismatched signatures, but does not prove forgery, replay, double-spend, consensus divergence, or state corruption.

## Search Motifs

- search for transaction signature length validation checks near cryptography entrypoints
- compare validation before and after the signature-format-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where RPC method execution, account scan, or transaction forwarding is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit validation for transaction signature-vector length in transaction verification paths before accepting or hashing the transaction.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
