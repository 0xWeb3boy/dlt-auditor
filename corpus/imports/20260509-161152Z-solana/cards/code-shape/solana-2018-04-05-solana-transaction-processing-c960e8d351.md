# Code-Shape Card

## Metadata

- ID: `solana-2018-04-05-solana-transaction-processing-c960e8d351`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `freshness-anchor-validation`

## Code Shape Summary

The patch changes accountant last_id handling so transaction validation fails closed for unknown last_id values instead of accepting and registering them on demand. The provided evidence supports a replay/freshness hardening finding, but does not prove a concrete double-spend, signature-forgery, or balance-bypass vulnerability.

## Search Motifs

- search for freshness anchor validation checks near transaction-processing entrypoints
- compare validation before and after the signature-and-signer-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for signed payload fields that are decoded but not bound to signer/domain/replay state

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Separate ledger entry registration from transaction validation, and fail closed when validation receives an unknown ledger freshness anchor.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The signature library or sanitized message type already commits the disputed field unconditionally.
