# Root-Cause Card

## Metadata

- ID: `reth-2026-02-03-reth-storage-4b9244c7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-trie-proof-generation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `complete-authenticated-proof-evidence`

## Violated Invariant

- Invariant: Proof builders must emit enough root or empty-root evidence to distinguish an empty subtrie from missing proof data, and stale reveal metadata must be invalidated after pruning.

## Trust Boundary

- Boundary: State/proof request inputs crossing into authenticated trie proof material returned to a verifier or caller.

## Attack Surface

- Entrypoint type: state-proof-generation
- Sensitive sink: Trie proof output and sparse-trie reveal cache.

## Impact Pattern

- Primary impact: Absence proofs carry explicit evidence instead of ambiguous empty output.
- Secondary impact: Subsequent proofs are rebuilt after pruning rather than reusing stale reveal state.

## Short Reusable Lesson

- Storage proof generation could omit root evidence for storage-only or empty-subtrie cases, and pruning could leave reveal metadata stale. The patch forces root-level evidence, emits explicit EmptyRoot markers, and clears revealed paths after pruning.
