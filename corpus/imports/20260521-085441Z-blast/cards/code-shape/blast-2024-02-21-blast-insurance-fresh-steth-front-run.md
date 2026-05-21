# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-insurance-fresh-steth-front-run`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `loss-eligibility-snapshot-gap`

## Code Shape Summary

- Bridge deposits mint L2 ETH or provider principal at stale/par value, while the later insurance/report path repairs the aggregate pool rather than only pre-loss holders.

## Search Motifs

- fresh stETH deposit
- known Lido slashing
- insuranceWithdrawalBuffer
- commitYieldReport(true)
- deposit admission not paused

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Pause or discount fresh deposits during known provider-loss windows and bind insurance eligibility to pre-loss accounting snapshots.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
