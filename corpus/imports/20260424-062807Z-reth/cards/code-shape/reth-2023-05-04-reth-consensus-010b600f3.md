# Code-Shape Card

## Metadata

- ID: `reth-2023-05-04-reth-consensus-010b600f3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-consensus-validation`

## Code Shape Summary

- The block admission path enforced only one direction of parent consistency in the shown code: number-to-hash lookup. The reverse condition, whether a canonical `parent_hash` also matched the claimed parent number, was not explicitly checked in the provided pre-patch path.

## Search Motifs

- authenticated trie/proof path drops empty-root, revealed-node, or rollback state needed for valid output
- fork-specific consensus rule selected from incomplete boundary inputs or generic validator
- search for `parent_hash` call sites that derive, cache, or validate security-sensitive state
- insufficient-consensus-validation fixes that add fail-closed validation before persistence, propagation, or canonicalization

## Typical Asymmetry

- Untrusted or fork-dependent input crosses consensus layer signal -> execution client forkchoice/block state, but protocol-rule-enforcement is incomplete before the code updates or relies on canonical head, payload status, or pipeline scheduling.

## Patch Pattern

- Add a reverse index lookup and enforce the missing consistency check at the block-admission boundary.

## False Match Warnings

- No proof that an attacker could trigger this through peer-supplied blocks in practice
- No demonstrated exploit, chain split, double-spend, or finality failure
- No tests or runtime evidence showing previously accepted invalid blocks
- A similar patch is lower risk if an earlier mandatory validator already rejects the malformed input before this path.
- Treat as provenance-only if the affected code is test-only, debug-only, or unreachable from peer/RPC/engine/sync inputs.
