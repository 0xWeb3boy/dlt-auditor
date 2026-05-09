# Code-Shape Card

## Metadata

- ID: `solana-2021-05-28-solana-consensus-2f7f243022`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `read-only-account-modification-bypass`

## Code Shape Summary

The patch fixes Solana BPF invocation permission enforcement so attempted modifications to read-only accounts are not hidden by deserialization behavior or account lookup source selection.

## Search Motifs

- search for read only account modification bypass checks near consensus entrypoints
- compare validation before and after the account-mutability-enforcement sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Deserialize account state needed for validation even when the account is read-only, then compare against the correct pre-invocation baseline and fail on unauthorized modification.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
