# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-socialized-gas-refunds-dev-fee-theft`
- Bug family: `resource_accounting_and_limits`
- Bug class: `global-refund-socialization`

## Code Shape Summary

- GasTracker scales every allocation by (gasUsed - refund) / gasUsed using a transaction-global refund number, losing which contract caused the refund.

## Search Motifs

- AllocateDevGas
- remainingGas := gasUsed - refund
- scaledGasUnits
- global refund counter
- SSTORE refund socialized

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Avoid user-controlled gas refunds in the accounting model or track refund source precisely enough that refunds only reduce the generating contract allocation.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
