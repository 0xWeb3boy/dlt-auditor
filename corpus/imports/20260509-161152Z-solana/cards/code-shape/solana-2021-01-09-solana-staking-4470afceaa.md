# Code-Shape Card

## Metadata

- ID: `solana-2021-01-09-solana-staking-4470afceaa`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `authority-model-hardening`

## Code Shape Summary

The evidence supports a BPF upgradeable loader change that adds explicit Buffer authority handling and immutable-buffer rejection, with related CLI routing for setting buffer authority. It does not support the heuristic baseline's staking, panic, denial-of-service, or consensus claims. This may be security-relevant authority-model work, but the vulnerability thesis is not established from the supplied hunks.

## Search Motifs

- search for authority model hardening checks near staking entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where account owner/write privilege, executable program state, or runtime syscall side effect is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit Buffer authority state handling at the loader instruction boundary and keep raw byte-write helpers limited to bounds-checked mutation, with authorization enforced by callers.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
