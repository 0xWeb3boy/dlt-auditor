# Root-Cause Card

## Metadata

- ID: `reth-2026-03-06-reth-storage-a1600ef0c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-integrity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `authenticated-state-proof-integrity`

## Violated Invariant

- Invariant: When masking trie branches for downstream proof or state-root work, a branch must not retain a cached child hash if masking leaves only one hashed child; the remaining child must be revealed so the branch can collapse into a structurally valid form.

## Trust Boundary

- Boundary: state database/proof request -> authenticated trie output

## Attack Surface

- Entrypoint type: trie-update/proof-generation-path
- Sensitive sink: state root, proof, or trie node persistence

## Impact Pattern

- Primary impact: proof-integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- When masking trie branches for downstream proof or state-root work, a branch must not retain a cached child hash if masking leaves only one hashed child; the remaining child must be revealed so the branch can collapse into a structurally valid form.
