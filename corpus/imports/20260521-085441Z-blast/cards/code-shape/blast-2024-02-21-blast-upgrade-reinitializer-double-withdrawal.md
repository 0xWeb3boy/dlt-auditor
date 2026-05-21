# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-upgrade-reinitializer-double-withdrawal`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `upgrade-reinitializer-reentrancy-reset`

## Code Shape Summary

- relayMessage sets xDomainMsgSender before the external call and marks success afterward; a reinitializer can reset the guard mid-call, allowing nested replay before success is recorded.

## Search Motifs

- xDomainMsgSender
- __CrossDomainMessenger_init
- reinitializer during relay
- failedMessages true
- successfulMessages after external call

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Do not reset active relay guards in upgrade initializers, and recheck successfulMessages or active relay state after the external target call returns.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
