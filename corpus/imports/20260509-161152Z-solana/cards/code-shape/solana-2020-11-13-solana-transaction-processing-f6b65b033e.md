# Code-Shape Card

## Metadata

- ID: `solana-2020-11-13-solana-transaction-processing-f6b65b033e`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-overflow-in-validation-counter`

## Code Shape Summary

The patch fixes overflow-sensitive arithmetic in `ledger/src/entry.rs` during tick hash count verification. The running `tick_hash_count` previously used direct `u64` addition and now uses `saturating_add`, so oversized cumulative counts cannot wrap before the exact equality check against `hashes_per_tick`.

## Search Motifs

- search for arithmetic overflow in validation counter checks near transaction-processing entrypoints
- compare validation before and after the checked-arithmetic-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Use overflow-safe arithmetic for validation counters that enforce protocol invariants.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
