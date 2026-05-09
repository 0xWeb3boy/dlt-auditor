# Code-Shape Card

## Metadata

- ID: `solana-2021-05-28-solana-consensus-a3240aebde`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `read-only-account-mutation`

## Code Shape Summary

The patch is a security fix for Solana BPF/CPI account handling. It strengthens detection of programs modifying read-only accounts by changing account lookup to prefer pre-instruction account state and by removing a deserialization path that skipped read-only account fields.

## Search Motifs

- search for read only account mutation checks near consensus entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Anchor mutation checks to pre-instruction account state and avoid skipping read-only account deserialization when those fields are needed for enforcement.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
