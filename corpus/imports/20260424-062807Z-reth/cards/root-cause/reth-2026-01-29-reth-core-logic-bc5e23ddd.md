# Root-Cause Card

## Metadata

- ID: `reth-2026-01-29-reth-core-logic-bc5e23ddd`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: Trie update operations should be atomic: if a leaf removal would require revealing blinded descendants during branch collapse, that reveal chain must be validated before mutation, and any failed update must restore values to their original subtrie so the trie is unchanged after error return.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-corruption

## Short Reusable Lesson

- Trie update operations should be atomic: if a leaf removal would require revealing blinded descendants during branch collapse, that reveal chain must be validated before mutation, and any failed update must restore values to their original subtrie so the trie is unchanged after error return.
