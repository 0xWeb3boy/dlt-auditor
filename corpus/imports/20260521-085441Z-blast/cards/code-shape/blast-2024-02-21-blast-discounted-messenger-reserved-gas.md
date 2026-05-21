# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-discounted-messenger-reserved-gas`
- Bug family: `resource_accounting_and_limits`
- Bug class: `bridge-failure-record-gas-underreserve`

## Code Shape Summary

- Messenger reserve gas was inherited from a path with fewer writes; Blast added discountedValues persistence on failure without increasing the relay reserve.

## Search Motifs

- RELAY_RESERVED_GAS
- failedMessages
- discountedValues
- SafeCall.callWithMinGas
- WithdrawalFinalized false

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Increase reserved gas or restructure finalization so failure replay state is written before value/lifecycle state is consumed.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
