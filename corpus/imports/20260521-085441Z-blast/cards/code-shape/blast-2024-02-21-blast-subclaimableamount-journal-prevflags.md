# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-subclaimableamount-journal-prevflags`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `incomplete-journal-rollback`

## Code Shape Summary

- SubClaimableAmount journals fixed/shares/remainder but omits prevFlags; rollback writes the zero-value flag, switching the account to YieldAutomatic.

## Search Motifs

- SubClaimableAmount
- balanceValuesChange
- prevFlags
- YieldAutomatic = 0
- RevertToSnapshot

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Include previous flags in every balance/yield journal entry and add revert-after-success tests for claimable yield operations.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
