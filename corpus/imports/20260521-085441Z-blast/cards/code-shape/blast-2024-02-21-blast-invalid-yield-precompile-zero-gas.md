# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-invalid-yield-precompile-zero-gas`
- Bug family: `resource_accounting_and_limits`
- Bug class: `invalid-precompile-revert-undercharge`

## Code Shape Summary

- Invalid precompile calls reach native selector parsing and revert handling while RequiredGas is zero and remaining gas is returned to the caller.

## Search Motifs

- invalid selector
- ErrExecutionReverted
- remainingGas == suppliedGas
- zero RequiredGas
- native precompile dispatch

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Charge a minimum invalid-call cost or make malformed dispatch consume the intended native precompile gas before returning a revert.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
