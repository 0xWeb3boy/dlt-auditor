# Code-Shape Card

## Metadata

- ID: `solana-2023-05-25-solana-transaction-processing-9d6c921b5f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `underconstrained-transaction-classification`

## Code Shape Summary

The patch tightens Solana sanitized transaction creation so automatic `is_simple_vote_tx` derivation requires `signatures.len() < 3` in addition to the existing legacy-message and single-instruction checks. The evidence supports a classification and validation hardening around simple vote transactions, but it does not establish an exploitable vulnerability or end-to-end security impact.

## Search Motifs

- search for underconstrained transaction classification checks near transaction-processing entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account balance/state mutation, fee/rent accounting, nonce state, or transaction commitment is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add a missing structural precondition to a transaction fast-path classifier and cover the rejected shape with regression tests.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
