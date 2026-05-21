# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-maker-dsr-shutdown-strands-dai`
- Bug family: `staking_registry_and_accountability`
- Bug class: `external-provider-shutdown-recovery-gap`

## Code Shape Summary

- The provider uses DSR_MANAGER.join/exit and values pieOf as recoverable, but lacks an alternate End.sol/Pot/DaiJoin shutdown recovery route.

## Search Motifs

- DSR_MANAGER.join
- DSR_MANAGER.exit
- pot.live
- daiJoin.live
- Maker Emergency Shutdown
- End.sol recovery

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Integrate directly with Maker shutdown redemption flows or add an audited emergency recovery path that can recover DAI when DSR_MANAGER exit is unavailable.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
