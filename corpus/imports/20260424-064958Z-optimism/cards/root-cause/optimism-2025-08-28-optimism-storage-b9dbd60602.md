# Root-Cause Card

## Metadata

- ID: `optimism-2025-08-28-optimism-storage-b9dbd60602`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: A reset checkpoint should only be used if its recorded L1 source block is still canonical on the current L1 chain; stale derived state from a reorged-out source must not be reused for reset.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-or-proof-integrity

## Short Reusable Lesson

- A reset checkpoint should only be used if its recorded L1 source block is still canonical on the current L1 chain; stale derived state from a reorged-out source must not be reused for reset. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
