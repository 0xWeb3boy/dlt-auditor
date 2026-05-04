# Code-Shape Card

## Metadata

- ID: `moonbeam-2022-09-12-moonbeam-staking-c7d8fc12f2`
- Bug family: `authz_and_role_gates`
- Bug class: `evm-precompile-authorization-boundary-hardening`

## Code Shape Summary

- The proxy precompile entered selector handling before checking caller code, and runtimes exposed a generic Dispatch precompile. The patch added caller-code rejection and removed Dispatch registration.

## Search Motifs

- precompile execute reads selector before caller eligibility check
- generic Dispatch precompile registered at fixed address
- pallet_evm::AccountCodes lookup added before runtime call bridge

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Add an early caller-code guard in the precompile and remove broad generic dispatch exposure from runtime precompile sets.

## False Match Warnings

- Contract callers may be safe if downstream origin conversion always denies privileged calls
- Precompile may be dev-only or disabled by runtime feature flags
- EOA-only checks are less relevant for read-only precompiles
