# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-native-yield-gas-refund-undermetering`
- Bug family: `resource_accounting_and_limits`
- Bug class: `native-bookkeeping-undermetering`

## Code Shape Summary

- Native yield mutates share/fixed/remainder fields and global share counts during ordinary balance operations, while gas-refund finalization iterates allocations and writes gas-parameter storage after EVM execution.

## Search Motifs

- SetBalance getSharePrice
- adjustShareCount
- BlastSharesAddress slot
- AllocateDevGas updateGasPredeploy
- opSelfdestruct native yield
- under-metered bookkeeping

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Benchmark and explicitly charge native-yield balance/share-count work and gas-refund finalizer work, including intrinsic or opcode-level surcharges that are not refunded back to attackers.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
