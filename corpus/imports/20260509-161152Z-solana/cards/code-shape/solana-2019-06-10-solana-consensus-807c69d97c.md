# Code-Shape Card

## Metadata

- ID: `solana-2019-06-10-solana-consensus-807c69d97c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `account-permission-invariant-hardening`

## Code Shape Summary

The patch adds explicit verification checks for non-debitable credit-only accounts and updates account storage to carry lamport-credit metadata. This is plausibly security relevant because it concerns runtime account authorization semantics, but the provided evidence does not establish a concrete vulnerability, exploit path, or production impact. It may be part of safely implementing or refactoring the credit-only account model.

## Search Motifs

- search for account permission invariant hardening checks near consensus entrypoints
- compare validation before and after the authorization-and-privilege-check sensitive sink
- trace equivalent paths: admission vs execution, live vs replay, and success vs failure handling
- look for authority checks in wrappers but not at the final state-changing sink

## Typical Asymmetry

- Validation is present on one path, layer, or representation but missing where bank freezing/rooting, tower vote decision, fork-choice state, or consensus-visible status is finally reached.
- Compare wrappers, replay/recovery, simulation, and fast paths against the canonical enforcement point.

## Patch Pattern

Add explicit invariant checks for a special account permission class and propagate the corresponding credit metadata through the storage boundary.

## False Match Warnings

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
- The account or authority is derived from trusted state and cannot be chosen by the caller.
