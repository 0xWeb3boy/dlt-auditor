# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-claimall-gas-nonoptimal-rate`
- Bug family: `resource_accounting_and_limits`
- Bug class: `claim-helper-nonoptimal-payout`

## Code Shape Summary

- The helper drains all gas using one rate calculation, while lower-level claims can split amount/seconds to obtain a better effective rate.

## Search Motifs

- claimAllGas
- claimGasAtMinClaimRate
- baseClaimRate
- ceilClaimRate
- gasSecondsToConsume

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Make claimAll compute the optimal payout over the claim curve or document it as non-optimal and expose safe helper semantics.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
