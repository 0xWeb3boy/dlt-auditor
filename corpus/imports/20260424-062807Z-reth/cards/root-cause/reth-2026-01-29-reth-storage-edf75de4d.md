# Root-Cause Card

## Metadata

- ID: `reth-2026-01-29-reth-storage-edf75de4d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `atomicity-violation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-update-atomicity`

## Violated Invariant

- Invariant: Sparse trie updates should not mutate structure unless all required reveal steps for the affected path are available, and a failed update should restore prior state to the same subtrie location it came from.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: none proven

## Short Reusable Lesson

- Sparse trie updates should not mutate structure unless all required reveal steps for the affected path are available, and a failed update should restore prior state to the same subtrie location it came from.
