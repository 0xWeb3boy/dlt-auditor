# Root-Cause Card

## Metadata

- ID: `optimism-2022-06-17-optimism-storage-35757456bf`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `oracle-output-key-mismatch`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `integrity-binding`

## Violated Invariant

- Invariant: If oracle outputs are consumed by block-specific proof or finality logic, all components must refer to the same canonical output identity for a given L2 block. The provided evidence shows an alignment from timestamp-derived lookup toward explicit L2 block numbers, but does not by itself establish a demonstrated security break.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: oracle-output-integrity
- Secondary impact: withdrawal-proof-integrity

## Short Reusable Lesson

- If oracle outputs are consumed by block-specific proof or finality logic, all components must refer to the same canonical output identity for a given L2 block. The provided evidence shows an alignment from timestamp-derived lookup toward explicit L2 block numbers, but does not by itself establish a demonstrated security break. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce integrity-binding at the boundary and fail closed before state, privilege, or.
