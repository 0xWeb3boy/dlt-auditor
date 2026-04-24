# Root-Cause Card

## Metadata

- ID: `optimism-2025-08-12-optimism-storage-84164c9019`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reorg-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: During L1 reorg handling, derivation state should only be rewound to a canonical L1 source block, and the search for that point should not go below the source block implied by finalized state.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- During L1 reorg handling, derivation state should only be rewound to a canonical L1 source block, and the search for that point should not go below the source block implied by finalized state. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
