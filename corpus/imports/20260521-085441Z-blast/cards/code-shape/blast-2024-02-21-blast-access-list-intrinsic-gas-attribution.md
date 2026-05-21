# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-access-list-intrinsic-gas-attribution`
- Bug family: `resource_accounting_and_limits`
- Bug class: `intrinsic-gas-attribution-mismatch`

## Code Shape Summary

- Intrinsic access-list gas is allocated to a global Blast gas address; the later warmed contract receives lower opcode gas and no corresponding intrinsic allocation.

## Search Motifs

- AccessListStorageKeyCost
- AccessListAddressCost
- IntrinsicGas
- BlastGasAddress
- warm storage attribution

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Attribute access-list intrinsic costs to the warmed targets or make access-list costs non-claimable by design with explicit accounting.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
