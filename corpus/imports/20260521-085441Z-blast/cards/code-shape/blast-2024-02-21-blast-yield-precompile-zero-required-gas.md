# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-yield-precompile-zero-required-gas`
- Bug family: `resource_accounting_and_limits`
- Bug class: `native-precompile-requiredgas-predicate`

## Code Shape Summary

- The selector table is placed under the wrong branch of selector parsing, so valid ABI calldata skips the intended per-selector gas costs and returns zero RequiredGas.

## Search Motifs

- RequiredGas
- readFunctionSelector
- err != nil
- valid selector returns 0
- RunPrecompiledContract subtracts RequiredGas

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Fix selector dispatch so valid selectors return their intended nonzero costs, and add tests for valid and invalid selector metering.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
