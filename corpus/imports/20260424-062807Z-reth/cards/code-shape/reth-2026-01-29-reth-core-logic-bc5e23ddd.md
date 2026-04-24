# Code-Shape Card

## Metadata

- ID: `reth-2026-01-29-reth-core-logic-bc5e23ddd`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`

## Code Shape Summary

- Failure handling in trie updates was not fully atomic. The code could begin structural mutation before proving that all required blinded-node reveals for branch collapse were available, and rollback bookkeeping could use the wrong subtrie location when restoring values after error.

## Search Motifs

- trie proof/update path drops empty-root, revealed-node, or rollback state needed for authenticated output
- state-integrity-hardening fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses execution/engine state transition -> persistent storage, but state-coordinate-consistency is incomplete before the code updates or relies on canonical database, trie updates, or state provider output.

## Patch Pattern

- Validate all error-prone structural prerequisites before mutating trie state, and record immutable original ownership/location so rollback restores state to the exact prior placement.

## False Match Warnings

- No proof that untrusted or network-reachable input can trigger the failing path
- No evidence that the corruption causes consensus divergence, state-root forgery, or fund impact
- No concrete exploit scenario or security advisory is provided
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
