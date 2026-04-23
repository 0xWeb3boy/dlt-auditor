# Root-Cause Card

## Metadata

- ID: `reth-2026-03-06-reth-storage-a1600ef0c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `proof-integrity`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch changes `MaskedTrieCursor::mask_node` so the last surviving hashed child is cleared whenever masking removes other hashed children, even if `state_mask` still contains unhashed children. The provided code and tests support a trie-structure correctness bug that previously left a stale single hashed child in place. The commit message says this caused debug panics and invalid proofs in release builds, but the supplied evidence does not establish a concrete security vulnerability beyond that correctness/integrity claim.
