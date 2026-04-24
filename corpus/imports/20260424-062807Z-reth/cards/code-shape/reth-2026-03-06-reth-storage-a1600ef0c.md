# Code-Shape Card

## Metadata

- ID: `reth-2026-03-06-reth-storage-a1600ef0c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-integrity`

## Code Shape Summary

- An overly narrow condition tied cleanup of the final surviving hashed child to the old `state_mask == hash_mask` case instead of the actual invariant: once masking leaves only one hashed child, that cached hash is no longer valid because the branch should collapse.

## Search Motifs

- cached execution or state object reused after parent hash, fork, or call context changes
- cached execution or state object reused after parent hash, fork, or call context changes
- trie proof/update path drops empty-root, revealed-node, or rollback state needed for authenticated output
- search for `MaskedTrieCursor::mask_node` call sites that derive, cache, or validate security-sensitive state
- search for `state_mask` call sites that derive, cache, or validate security-sensitive state

## Typical Asymmetry

- Untrusted or fork-dependent input crosses state database/proof request -> authenticated trie output, but authenticated-state-proof-integrity is incomplete before the code updates or relies on state root, proof, or trie node persistence.

## Patch Pattern

- Remove a special-case guard and enforce the structural post-update invariant directly in the masking logic.

## False Match Warnings

- No evidence shows untrusted input or attacker-controlled reachability to this path
- No downstream verification or consensus failure is demonstrated in the patch itself
- No concrete exploit scenario, privilege impact, or acceptance of forged state is shown
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
