# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-eoa-nocode-custom-surcharge`
- Bug family: `resource_accounting_and_limits`
- Bug class: `nocode-target-repeated-surcharge`

## Code Shape Summary

- No-code calls return without target execution or allocation, but the repeated surcharge predicate only checks whether the target has an allocation.

## Search Motifs

- empty code
- EOA target
- GetCodeHash zero
- GetGasUsedByContract(addr) == 0
- repeated no-code calls

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Do not charge the storage-style surcharge for no-code targets, or record an explicit per-target surcharge marker independent of execution allocation.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
