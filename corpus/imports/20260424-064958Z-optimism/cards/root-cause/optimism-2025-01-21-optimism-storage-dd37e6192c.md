# Root-Cause Card

## Metadata

- ID: `optimism-2025-01-21-optimism-storage-dd37e6192c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-state-transition-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: Persisted supervisor state should bind rewind and derivation transitions to exact block identities and should not continue past an invalidated derived entry until a checked replacement is installed.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-or-proof-integrity

## Short Reusable Lesson

- Persisted supervisor state should bind rewind and derivation transitions to exact block identities and should not continue past an invalidated derived entry until a checked replacement is installed. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
