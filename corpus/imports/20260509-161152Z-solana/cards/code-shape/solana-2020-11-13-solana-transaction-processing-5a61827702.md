# Code-Shape Card

## Metadata

- ID: `solana-2020-11-13-solana-transaction-processing-5a61827702`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `integer-overflow`

## Code Shape Summary

The patch fixes overflow-prone arithmetic in Solana ledger entry tick hash verification. `verify_tick_hash_count` previously added each `entry.num_hashes` into a `u64` accumulator with `+=` before checking tick boundaries. The fix uses `saturating_add`, so excessive cumulative hash counts remain excessive instead of wrapping to a smaller value.

## Search Motifs

- search for integer overflow checks near transaction-processing entrypoints
- compare validation before and after the checked-arithmetic-bounds sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Use saturating arithmetic for validation accumulators where later checks depend on monotonic cumulative counts.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
