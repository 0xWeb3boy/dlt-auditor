# Code-Shape Card

## Metadata

- ID: `solana-2020-01-15-solana-cryptography-b16c30b4c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-hash-alignment-bug`

## Code Shape Summary

The patch fixes an offset mismatch in `AccountsDB::store_accounts`. Before the change, remaining account metadata was sliced with `infos.len()` after partial append progress, but the hashes argument still started at the beginning of the original hash slice. After the change, hashes are sliced with the same offset, preserving account-to-hash alignment. The commit message and added bank-hash test support a consensus/liveness relevance, but the provided ev...

## Search Motifs

- search for state hash alignment bug checks near cryptography entrypoints
- compare validation before and after the state-root-consistency sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for state transitions where observation and enforcement use different coordinates

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where canonical bank state, account storage, snapshot acceptance, or ledger root is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

When passing parallel slices through retry, chunking, or partial-progress logic, apply the same progress offset to every positionally coupled input.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
