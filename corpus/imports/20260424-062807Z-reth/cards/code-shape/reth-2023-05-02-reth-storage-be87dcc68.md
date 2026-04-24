# Code-Shape Card

## Metadata

- ID: `reth-2023-05-02-reth-storage-be87dcc68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-target-mismatch`

## Code Shape Summary

- Persisted Merkle rebuild progress was not strictly bound to the current rebuild target at the resume/save boundary, and stale checkpoint metadata was not explicitly invalidated before a fresh rebuild.

## Search Motifs

- cached execution or state object reused after parent hash, fork, or call context changes
- checkpoint-target-mismatch fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but checkpoint-target-binding is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- Validate persisted resume state against the current execution target, invalidate stale checkpoint metadata before restarting, and persist future checkpoints with explicit target context.

## False Match Warnings

- No proof that a remote peer or attacker could intentionally trigger the stale-checkpoint condition
- No test, incident report, or reproduction showing invalid state roots, bad block acceptance, or consensus divergence before the fix
- No evidence that the pre-fix behavior led to more than incorrect resume behavior, wasted work, or local rebuild inconsistency
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
