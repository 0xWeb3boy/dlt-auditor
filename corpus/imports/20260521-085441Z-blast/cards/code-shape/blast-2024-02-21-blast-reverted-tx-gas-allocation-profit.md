# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-reverted-tx-gas-allocation-profit`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `non-rollbacked-sidecar-accounting`

## Code Shape Summary

- StateDB snapshots roll back storage/logs/refunds, but the transaction-local GasTracker allocation map is not journaled and is finalized anyway.

## Search Motifs

- ErrExecutionReverted
- RevertToSnapshot
- GasTracker not journaled
- AllocateDevGas after vmerr
- claimable gas on failed tx

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Snapshot or roll back gas attribution entries for reverted frames, or define/restrict claimability for failed work explicitly.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
