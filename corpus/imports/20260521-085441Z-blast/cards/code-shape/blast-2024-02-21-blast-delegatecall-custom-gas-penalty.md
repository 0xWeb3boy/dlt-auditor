# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-delegatecall-custom-gas-penalty`
- Bug family: `resource_accounting_and_limits`
- Bug class: `delegatecall-surcharge-identity-mismatch`

## Code Shape Summary

- The high-frame surcharge checks whether the target library address has allocation, but delegatecall/callcode execution and gas attribution use the caller context.

## Search Motifs

- DELEGATECALL
- CALLCODE
- contract.Address()
- target addr predicate
- GetGasUsedByContract(target) == 0

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- For delegatecall/callcode, key the surcharge predicate to the allocation address or suppress target-first-use penalties that cannot create target allocation.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
