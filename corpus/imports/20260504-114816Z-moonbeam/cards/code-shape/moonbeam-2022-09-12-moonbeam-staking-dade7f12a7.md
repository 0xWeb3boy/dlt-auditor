# Code-Shape Card

## Metadata

- ID: `moonbeam-2022-09-12-moonbeam-staking-dade7f12a7`
- Bug family: `authz_and_role_gates`
- Bug class: `evm-precompile-access-control-hardening`

## Code Shape Summary

- The EVM precompile boundary lacked a reusable caller eligibility check for code-bearing accounts. The fix queries AccountCodes before selector handling and removes the Dispatch precompile.

## Search Motifs

- handle.context().caller used only after selector dispatch
- AddressU64 dispatch precompile in runtime precompile registry
- tests expect smart contract caller to revert

## Typical Asymmetry

- The accepting path trusted a local or current-state predicate, while the sensitive sink required a stronger global, historical, caller-class, domain, or cumulative invariant.

## Patch Pattern

- Fail early for disallowed contract callers and narrow the runtime precompile surface by unregistering generic dispatch.

## False Match Warnings

- Some precompiles intentionally support contract callers and are safe if read-only
- A no-code sentinel account exception may be valid
- Unregistered precompile addresses in production configs are not exploitable
