# Root-Cause Card

## Metadata

- ID: `optimism-2025-08-28-optimism-storage-2ba747f98b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-canonicality-validation`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: A local_safe block used as a reset anchor must still map to a canonical L1 source block; if its recorded source is no longer canonical after an L1 reorg, reset should not proceed from that anchor.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- A local_safe block used as a reset anchor must still map to a canonical L1 source block; if its recorded source is no longer canonical after an L1 reorg, reset should not proceed from that anchor. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
