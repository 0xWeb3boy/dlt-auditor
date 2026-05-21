# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-saved-etherseconds-gas-refund-dos`
- Bug family: `resource_accounting_and_limits`
- Bug class: `gas-refund-maturity-reuse`

## Code Shape Summary

- Gas accounting stores claimable gas value and maturity seconds separately; a full-balance claim consumes only the seconds needed for the selected payout rate and can leave reusable maturity behind.

## Search Motifs

- etherSeconds
- claimAllGas
- claimMaxGas
- gasToClaim * ceilGasSeconds
- updateGasPredeploy
- maturity seconds survive zero balance

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- When claimable gas balance is fully withdrawn, clear or cap the associated maturity seconds so old seconds cannot apply to newly accrued gas.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
