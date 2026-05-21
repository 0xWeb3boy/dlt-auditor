# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-l1-da-fee-undercharge-discounted-withdrawal`
- Bug family: `resource_accounting_and_limits`
- Bug class: `fee-recovery-discount-mismatch`

## Code Shape Summary

- The same discounted withdrawal mechanism used for user ETH is applied to fee vault balances collected for L1 data costs.

## Search Motifs

- L1FeeVault
- l1 data fee
- withdraw threshold
- sharePrice discount
- operator cost recovery

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Separate fee-vault settlement from user yield-discount settlement or account the discount explicitly in fee charging.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
