# Code-Shape Card

## Metadata

- ID: `solana-2022-02-24-solana-storage-97d40ba3da`
- Bug family: `authz_and_role_gates`
- Bug class: `rent-state-validation-bypass`

## Code Shape Summary

The patch likely fixes a runtime rent-state validation bypass. The central supported change is in `runtime/src/account_rent_state.rs`, where `RentState::transition_allowed_from` now carries `do_support_realloc` and compares pre/post data sizes for `RentPaying(data_size)` accounts. This supports the commit subject that resized accounts must be rent exempt. The evidence does not support the heuristic claims about panics, malformed decoding, cryptographic...

## Search Motifs

- search for rent state validation bypass checks near storage entrypoints
- compare validation before and after the input-shape-validation sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Preserve enough state for post-transaction validation to distinguish unchanged legacy rent-paying accounts from resized rent-paying accounts, and reject the resized-below-rent-exempt case.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
