# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-weth-rebasing-genesis-zero-share-price`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `initializer-genesis-state-mismatch`

## Code Shape Summary

- Direct genesis storage sets initialized flags and native yield mode, but does not seed the WETH rebasing token price that normal initialize would set from Shares.price.

## Search Motifs

- NewL2StorageConfig
- _initialized = 1
- WETHRebasing.initialize
- price not set
- _totalShares == 0
- _addValue returns

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Execute the initializer during genesis or write every initializer-equivalent storage field, including price, metadata, and Blast config.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
