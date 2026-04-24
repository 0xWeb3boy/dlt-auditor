# Root-Cause Card

## Metadata

- ID: `optimism-2025-01-28-optimism-transaction-processing-d39eb247e6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: Host-triggered L2 block re-execution should run with the intended L2 key-value store available, and preimage writes should use the expected 32-byte hash-key format, so replay data is handled consistently.

## Trust Boundary

- Boundary: persisted chain state -> recovery/derivation logic

## Attack Surface

- Entrypoint type: state-storage or reset/reorg handling path
- Sensitive sink: stored canonicality, proof-window, or derived-state update

## Impact Pattern

- Primary impact: integrity
- Secondary impact: state-integrity

## Short Reusable Lesson

- Host-triggered L2 block re-execution should run with the intended L2 key-value store available, and preimage writes should use the expected 32-byte hash-key format, so replay data is handled consistently. Similar bugs appear when state-storage or reset/reorg handling path code treats partially checked input as authoritative and lets it reach stored canonicality, proof-window, or derived-state update. The reusable fix is to enforce input-validation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
