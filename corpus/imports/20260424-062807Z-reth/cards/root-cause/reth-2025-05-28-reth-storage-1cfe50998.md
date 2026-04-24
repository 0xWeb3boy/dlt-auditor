# Root-Cause Card

## Metadata

- ID: `reth-2025-05-28-reth-storage-1cfe50998`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: When canonical blocks are prepared for persistence, the in-memory branch should not rely on missing trie-update data for itself or its ancestors; if required derived trie/state data is absent, persistence should detect that condition and handle it explicitly instead of assuming the data already exists.

## Trust Boundary

- Boundary: execution/engine state transition -> persistent storage

## Attack Surface

- Entrypoint type: state-storage-update-path
- Sensitive sink: canonical database, trie updates, or state provider output

## Impact Pattern

- Primary impact: state-integrity-risk
- Secondary impact: state-integrity

## Short Reusable Lesson

- When canonical blocks are prepared for persistence, the in-memory branch should not rely on missing trie-update data for itself or its ancestors; if required derived trie/state data is absent, persistence should detect that condition and handle it explicitly instead of assuming the data already exists.
