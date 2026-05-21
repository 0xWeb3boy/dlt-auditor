# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-address-keyed-governor-redeploy`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `durable-address-keyed-configuration`

## Code Shape Summary

- Blast authorization is keyed by address only; create/redeploy/proxy lifecycle can change code while governor and gas/yield state persist outside the contract storage.

## Search Motifs

- governorMap[address]
- CREATE2 redeploy
- selfdestruct then redeploy
- configureContract
- address-keyed gas params

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Clear/rebind external gas/yield config on code identity changes or require deployments to opt into durable address-lifetime ownership explicitly.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
