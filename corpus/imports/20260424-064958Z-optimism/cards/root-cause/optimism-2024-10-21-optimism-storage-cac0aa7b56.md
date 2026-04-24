# Root-Cause Card

## Metadata

- ID: `optimism-2024-10-21-optimism-storage-cac0aa7b56`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-frontier-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Cross-unsafe state should advance only to the next stored block that directly extends the currently tracked cross-unsafe head by parent hash, with explicit handling for missing start state and frontier queries.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-or-proof-integrity

## Short Reusable Lesson

- Cross-unsafe state should advance only to the next stored block that directly extends the currently tracked cross-unsafe head by parent hash, with explicit handling for missing start state and frontier queries. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
