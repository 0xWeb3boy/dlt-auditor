# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-high-frame-precompile-surcharge-repeat`
- Bug family: `resource_accounting_and_limits`
- Bug class: `custom-surcharge-wrong-participant-key`

## Code Shape Summary

- The surcharge predicate checks target allocation, but precompile work is attributed to a global Blast address rather than the target, so the target always looks first-use.

## Search Motifs

- BlastGasParamStorageGas
- BlastMaxFrameCount
- GetGasUsedByContract(precompile)
- precompile attribution to BlastGasAddress

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Track a separate seen/surcharged target set or bind the predicate to the same participant identity that receives the allocation.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
