# Code-Shape Card

## Metadata

- ID: `blast-2024-02-21-blast-uninitialized-usd-yield-manager-implementation`
- Bug family: `authz_and_role_gates`
- Bug class: `unlocked-proxy-implementation-initializer`

## Code Shape Summary

- ETHYieldManager locks its implementation in the constructor, while USDYieldManager leaves the Initializable path open; owner-only addProvider can delegatecall attacker-controlled provider code.

## Search Motifs

- constructor does not call initialize
- _disableInitializers missing
- initializer on implementation
- addProvider delegatecall
- selfdestruct in provider initialize

## Typical Asymmetry

- A security or accounting invariant is implemented in the common path but missing in a direct bridge path, revert path, helper path, native precompile path, provider-loss path, or upgrade/genesis path.

## Patch Pattern

- Lock implementation initializers in constructors and avoid exposing implementation-local ownership paths that can reach delegatecall-capable plugins.

## False Match Warnings

- The same property is enforced earlier on every reachable path before state, gas, or value is committed.
- The actor who can trigger the path already owns the affected role, funds, or address-lifecycle authority.
- The behavior is explicitly documented and all downstream accounting prices it as an intended policy choice.
- The path is test-only, deployment-local, or requires an operator-only misconfiguration with no protocol effect.
