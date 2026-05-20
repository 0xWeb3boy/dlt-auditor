# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2025-01-mr-h01-statedb-pointer-not-cleared`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `statedb-pointer-lifecycle-cleanup-missing`

## Code Shape Summary

- A post-contest mitigation still assigned the bank StateDB pointer in precompile paths but did not reliably clear it back to nil after execution.

## Search Motifs

- Bank.StateDB set but not nilled
- precompile funtoken NewStateDB lifecycle
- SyncStateDBWithAccount sees stale StateDB
- ensure stateDB is nil after tx execution

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Add lifecycle cleanup that sets the bank StateDB pointer to nil after tx or precompile execution on all paths.

## False Match Warnings

- No issue if StateDB is passed through context only.
- No issue if a defer always clears the pointer on every return path.
- No issue if nil vs non-nil does not affect consensus-visible execution.
