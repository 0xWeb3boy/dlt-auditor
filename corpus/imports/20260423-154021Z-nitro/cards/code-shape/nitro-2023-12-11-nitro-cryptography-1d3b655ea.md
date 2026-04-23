# Code-Shape Card

## Metadata

- ID: `nitro-2023-12-11-nitro-cryptography-1d3b655ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-state-commitment`

## Code Shape Summary

- Short description of what the buggy code looked like: The strongest supported finding is a prover state-hash correctness fix: `Machine::hash` now commits the guard-enabled flag even when the guard stack is empty, and `ErrorGuardProof::hash_guards` no longer mixes that flag into the stack-hash helper.

## Search Motifs

- Motif 1: state hashes include a collection hash but omit the mode bit that changes semantics when the collection is empty
- Motif 2: helper hash functions mix collection contents with unrelated top-level state flags
- Motif 3: patches move a flag from helper hashing into the top-level machine hash function

## Typical Asymmetry

- What was checked in one path but missing in another: A cached, implicit, or convenience state source was accepted as if it were canonical, while the later sink depended on stronger identity, boundary, or chain-binding guarantees that were not actually enforced there.

## Patch Pattern

- What the fix changed structurally: Move mode or feature flags into the top-level state commitment and keep collection-hash helpers responsible only for collection contents.

## False Match Warnings

- What looks similar but is often not a bug: If all later sinks independently recompute the same canonical state from finalized inputs, similar cases may remain correctness-only.
