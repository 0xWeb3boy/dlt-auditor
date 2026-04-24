# Code-Shape Card

## Metadata

- ID: `reth-2026-02-03-reth-storage-4b9244c7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-trie-proof-generation`

## Code Shape Summary

- The direct root cause shown by the snippets is inconsistent proof-generation and cache-invalidation behavior around empty storage subtries and pruned sparse tries. Root or empty-root evidence was not consistently preserved for all storage proof requests, and reveal metadata could remain after pruning changed the underlying trie representation.

## Search Motifs

- cached execution or state object reused after parent hash, fork, or call context changes
- cached execution or state object reused after parent hash, fork, or call context changes
- trie proof/update path drops empty-root, revealed-node, or rollback state needed for authenticated output
- incomplete-trie-proof-generation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses state database/proof request -> authenticated trie output, but authenticated-state-proof-integrity is incomplete before the code updates or relies on state root, proof, or trie node persistence.

## Patch Pattern

- Return explicit root or EmptyRoot proof material for empty/non-existent storage subtries and invalidate proof-generation caches when pruning changes trie node representation.

## False Match Warnings

- No reproducer showing that pre-patch proofs were accepted incorrectly across a trust boundary
- No test or commit message tying the bug to an attack scenario, consensus issue, or verifier bypass
- No evidence that remote attackers could trigger or weaponize the ambiguous proof output
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
