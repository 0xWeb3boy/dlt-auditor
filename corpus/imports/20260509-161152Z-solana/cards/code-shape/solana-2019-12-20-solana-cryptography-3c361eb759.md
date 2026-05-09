# Code-Shape Card

## Metadata

- ID: `solana-2019-12-20-solana-cryptography-3c361eb759`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `snapshot-integrity-validation`

## Code Shape Summary

The patch strengthens Solana snapshot/account verification by adding a per-account hash check in `runtime/src/accounts_db.rs::verify_bank_hash`. Before aggregation, the verifier now recomputes each non-sysvar account hash and returns `MismatchedAccountHash` if it differs from the stored `account.hash`. The `sdk/src/hash.rs` changes from literal `32` to `HASH_BYTES` are supporting cleanup and are not independent vulnerability evidence.

## Search Motifs

- search for snapshot integrity validation checks near cryptography entrypoints
- compare validation before and after the snapshot-integrity-binding sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Validate underlying leaf state before accepting a derived aggregate integrity check.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
