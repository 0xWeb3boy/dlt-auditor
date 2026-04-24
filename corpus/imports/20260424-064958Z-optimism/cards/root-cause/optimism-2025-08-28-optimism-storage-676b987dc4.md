# Root-Cause Card

## Metadata

- ID: `optimism-2025-08-28-optimism-storage-676b987dc4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: A reset target chosen from stored derivation state should still map to a canonical L1 source block at the time of reset.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-or-proof-integrity

## Short Reusable Lesson

- A reset target chosen from stored derivation state should still map to a canonical L1 source block at the time of reset. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
