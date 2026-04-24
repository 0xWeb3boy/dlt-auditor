# Root-Cause Card

## Metadata

- ID: `optimism-2026-02-09-optimism-transaction-processing-68b81dd5bb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finalization-boundary-check`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-state-invariant`

## Violated Invariant

- Invariant: The rewind helper should not return targets older than the current finalized L2 head. The provided evidence establishes this as a local rewind-path invariant, but does not prove a broader security property or exploit path.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: finalization-invariant-protection
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- The rewind helper should not return targets older than the current finalized L2 head. The provided evidence establishes this as a local rewind-path invariant, but does not prove a broader security property or exploit path. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce protocol-state-invariant at the boundary and fail closed before state, privilege, or consensus-visible output changes.
