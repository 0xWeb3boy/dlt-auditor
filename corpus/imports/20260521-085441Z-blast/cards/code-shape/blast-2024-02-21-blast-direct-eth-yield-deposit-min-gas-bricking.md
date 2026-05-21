# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-direct-eth-yield-deposit-min-gas-bricking`
- Bug family: `resource_accounting_and_limits`
- Bug class: `bridge-direct-deposit-gas-budget`

## Code Shape Summary

- A direct deposit path sends portal value and finalizer calldata with user-provided minGasLimit, but the L2 finalizer has no messenger failed-message state or replay handle.

## Search Motifs

- finalizeBridgeETHDirect
- depositTransaction
- _minGasLimit
- direct ETH yield token bridge
- no failedMessages replay

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Compute a mandatory base gas floor for the direct finalizer or route value-bearing deposits through a replayable messenger path.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
