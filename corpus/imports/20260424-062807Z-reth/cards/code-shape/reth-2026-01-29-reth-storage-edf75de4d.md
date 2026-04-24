# Code-Shape Card

## Metadata

- ID: `reth-2026-01-29-reth-storage-edf75de4d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `atomicity-violation`

## Code Shape Summary

- The code allowed mutation to begin before all reveal dependencies for branch collapse were known to be available, and its rollback bookkeeping did not preserve enough location metadata to restore the previous state exactly after a blinded-node error.

## Search Motifs

- trie proof/update path drops empty-root, revealed-node, or rollback state needed for authenticated output
- atomicity-violation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but state-update-atomicity is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- Move prerequisite validation ahead of mutation, and capture enough immutable origin metadata to perform exact rollback on retriable errors.

## False Match Warnings

- No proof that an external attacker can reliably trigger the blinded-node failure path
- No evidence of acceptance of invalid state, consensus split, replay issue, or cross-node security impact
- No reproducer, exploit scenario, or test demonstrating security consequences beyond local inconsistency/corruption risk
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
