# Root-Cause Card

## Metadata

- ID: `optimism-2026-04-10-optimism-storage-bc9c3420ae`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: The evidenced invariant is local proof-window consistency: mutations should only proceed when the proof window is initialized, new blocks should attach to the stored latest hash, and reorg replacement should stay within the stored earliest/latest window. The provided material does not establish a broader protocol-security failure.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-or-proof-integrity

## Short Reusable Lesson

- The evidenced invariant is local proof-window consistency: mutations should only proceed when the proof window is initialized, new blocks should attach to the stored latest hash, and reorg replacement should stay within the stored earliest/latest window. The provided material does not establish a broader protocol-security failure. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or.
