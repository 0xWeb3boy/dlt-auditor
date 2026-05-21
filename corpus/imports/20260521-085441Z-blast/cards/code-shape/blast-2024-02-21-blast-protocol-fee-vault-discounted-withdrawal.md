# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-protocol-fee-vault-discounted-withdrawal`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `fee-vault-discount-domain-mismatch`

## Code Shape Summary

- Fee vault balances are nominal protocol fees on L2 but are withdrawn through the same discounted user ETH queue used for yield losses.

## Search Motifs

- FeeVault.withdraw
- permissionless withdrawal
- sharePrice < 1e27
- protocol fee bucket
- discountedValues

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Route protocol fee vaults through nominal-value settlement or explicitly account/document their participation in negative-yield socialization.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
