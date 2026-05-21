# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-lido-oracle-cap-withdrawal-overpayment`
- Bug family: `attestation_trust_and_freshness`
- Bug class: `external-oracle-loss-lag`

## Code Shape Summary

- Share price depends on provider totalValue and accumulatedNegativeYields, but Lido losses are only realized after oracle/report/claim sequencing.

## Search Motifs

- oracle cap
- sharePrice still 1e27
- accumulatedNegativeYields
- finalize before loss report
- Lido slash

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Require fresh provider loss reporting/claiming before finalization, especially around oracle-capped or delayed-loss windows.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
