# Root-Cause Card

## Metadata

- ID: `optimism-2025-03-14-optimism-storage-d6a49f70d3`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-verification-binding`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Verification of an initiating log or executing access condition should be bound to the full checked context and reject mismatched timestamp/context data before returning success.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: verification-bypass-risk
- Secondary impact: security-hardening-or-correctness

## Short Reusable Lesson

- Verification of an initiating log or executing access condition should be bound to the full checked context and reject mismatched timestamp/context data before returning success. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
