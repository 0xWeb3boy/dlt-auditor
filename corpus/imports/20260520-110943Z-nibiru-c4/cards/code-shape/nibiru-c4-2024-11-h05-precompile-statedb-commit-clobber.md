# Code-Shape Card

## Metadata

- ID: `nibiru-c4-2024-11-h05-precompile-statedb-commit-clobber`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `precompile-statedb-commit-clobber`

## Code Shape Summary

- FunToken precompile nested calls updated a cache context while outer EthereumTx committed stale or dirtied StateDB objects back over those changes.

## Search Motifs

- multiple new StateDBs in ApplyEvmMsg
- reset StateDB back to original near precompile end
- getStateObject uses evmTxCtx instead of cacheCtx
- sendToBank then ERC20 transfer dirties storage

## Typical Asymmetry

- The trusted protocol side assumes a helper, cache, callback, token, meter, or account state is already safe; the attacker controls the input, ordering, token behavior, query, or nested call that reaches the trusted sink.

## Patch Pattern

- Ensure only one StateDB copy is active during an Ethereum transaction and that nested precompile calls preserve dirty state in the same commit path.

## False Match Warnings

- No issue if nested calls share one StateDB and one commit context.
- No issue if dirty state is refreshed from the latest cache context before commit.
- No issue if precompile cannot invoke user-controlled ERC20 callbacks.
