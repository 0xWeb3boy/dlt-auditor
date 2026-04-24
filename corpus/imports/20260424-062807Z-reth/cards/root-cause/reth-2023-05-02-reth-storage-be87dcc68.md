# Root-Cause Card

## Metadata

- ID: `reth-2023-05-02-reth-storage-be87dcc68`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `checkpoint-target-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `checkpoint-target-binding`

## Violated Invariant

- Invariant: If the Merkle stage resumes a multi-step trie rebuild from persisted progress, that checkpoint must correspond to the same `to_block` as the rebuild currently being executed; otherwise persisted progress and the rebuild target can diverge.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- If the Merkle stage resumes a multi-step trie rebuild from persisted progress, that checkpoint must correspond to the same `to_block` as the rebuild currently being executed; otherwise persisted progress and the rebuild target can diverge.
