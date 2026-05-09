# Code-Shape Card

## Metadata

- ID: `solana-2022-01-28-solana-validator-ops-a71f05f86c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `cpi-duplicate-account-privilege-escalation`

## Code Shape Summary

The patch fixes CPI duplicate account privilege handling in Solana's instruction preparation path. Duplicate account metas are normalized by merging privilege bits, so privilege checks must be applied after deduplication to the final effective account entry. The supplied implementation evidence directly shows writable privilege validation moved from inside the deduplication loop to a post-deduplication pass; signer coverage is supported by the commit me...

## Search Motifs

- search for cpi duplicate account privilege escalation checks near validator-ops entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where stake delegation, withdrawal, reward accounting, vote authority, or validator weight is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Normalize duplicate account references first, compute the final effective privilege set, then enforce CPI privilege invariants against that normalized state.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
