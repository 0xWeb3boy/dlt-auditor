# Root-Cause Card

## Metadata

- ID: `optimism-2025-07-08-optimism-storage-ebb9f7cfcc`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `derivation-state-consistency`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: No security-specific invariant is established by the provided evidence. The visible invariant is operational: when processing a non-newer derived block pair, the supervisor should compare against stored state at that same derived height, and reset-related errors should be surfaced rather than ignored.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: state-integrity
- Secondary impact: state-or-proof-integrity

## Short Reusable Lesson

- No security-specific invariant is established by the provided evidence. The visible invariant is operational: when processing a non-newer derived block pair, the supervisor should compare against stored state at that same derived height, and reset-related errors should be surfaced rather than ignored. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output.
