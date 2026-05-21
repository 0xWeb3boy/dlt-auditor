# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-access-list-warmth-custom-surcharge`
- Bug family: `resource_accounting_and_limits`
- Bug class: `access-list-custom-gas-incompatibility`

## Code Shape Summary

- The standard cold-account cost respects access-list warmth, but the Blast high-frame surcharge ignores that warmth and can still add storage-style gas.

## Search Motifs

- accessList
- AddressInAccessList
- warm target
- BlastGasParamStorageGas
- frameCount > BlastMaxFrameCount

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Integrate access-list warmth into the custom surcharge or expose/document a separate gas rule that callers can estimate reliably.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
