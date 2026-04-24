# Root-Cause Card

## Metadata

- ID: `reth-2026-02-03-reth-storage-4b9244c7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-trie-proof-generation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authenticated-state-proof-integrity`

## Violated Invariant

- Invariant: Trie proof generation must return enough structure to distinguish an actually empty or non-existent subtrie from omitted proof material, and pruning that converts revealed nodes back to hash stubs must invalidate reveal bookkeeping before later proofs are built.

## Trust Boundary

- Boundary: state database/proof request -> authenticated trie output

## Attack Surface

- Entrypoint type: trie-update/proof-generation-path
- Sensitive sink: state root, proof, or trie node persistence

## Impact Pattern

- Primary impact: proof-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Trie proof generation must return enough structure to distinguish an actually empty or non-existent subtrie from omitted proof material, and pruning that converts revealed nodes back to hash stubs must invalidate reveal bookkeeping before later proofs are built.
