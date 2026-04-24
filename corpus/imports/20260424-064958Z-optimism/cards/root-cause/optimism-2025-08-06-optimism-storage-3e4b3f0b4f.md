# Root-Cause Card

## Metadata

- ID: `optimism-2025-08-06-optimism-storage-3e4b3f0b4f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unsafe-state-rewind`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: A log-only rewind must not delete logs at or below the current LocalSafe head, because that would let persisted logs diverge from the recorded safety state.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-or-proof-integrity

## Short Reusable Lesson

- A log-only rewind must not delete logs at or below the current LocalSafe head, because that would let persisted logs diverge from the recorded safety state. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
