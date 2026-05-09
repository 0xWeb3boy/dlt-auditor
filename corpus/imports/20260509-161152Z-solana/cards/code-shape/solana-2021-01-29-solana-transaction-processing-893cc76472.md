# Code-Shape Card

## Metadata

- ID: `solana-2021-01-29-solana-transaction-processing-893cc76472`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-invariant-bypass`

## Code Shape Summary

The patch strengthens upgradeable BPF loader authorization by requiring the buffer authority to match the upgrade authority for deploy and upgrade operations under the matching_buffer_upgrade_authorities feature. It also prevents setting buffer authority to None under the same feature and updates CLI behavior and tests around that invariant.

## Search Motifs

- search for authorization invariant bypass checks near transaction-processing entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add an explicit feature-gated authority-equality guard in the loader path and reject authority states that cannot satisfy the new invariant.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
