# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-pending-balance-withdrawal-shareprice`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-provider-loss-checkpoint`

## Code Shape Summary

- Provider totalValue includes pendingBalance at nominal value, while realized negative yield is only recorded when claim/report hooks process exits.

## Search Motifs

- pendingBalance
- claimable Lido exits
- finalize before commitYieldReport
- claimBatchSize
- sharePrice checkpoint

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Before finalizing withdrawals, force provider claim/report freshness or block finalization while claimable below-par exits remain unprocessed.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
