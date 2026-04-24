# Root-Cause Card

## Metadata

- ID: `optimism-2025-05-19-optimism-consensus-1681ca2942`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `path-confinement`

## Violated Invariant

- Invariant: During EL sync startup, the node must not mark the current unsafe L2 head as safe or finalized just because sync progressed or a recovery path was taken; startup forkchoice should be derived from an older eligible L2 block based on L1-origin context, or from genuinely finalized state.

## Trust Boundary

- Boundary: artifact/archive input -> host filesystem

## Attack Surface

- Entrypoint type: archive-extraction or file-materialization path
- Sensitive sink: filesystem write outside the intended extraction or artifact directory

## Impact Pattern

- Primary impact: incorrect-forkchoice-state
- Secondary impact: consensus-integrity

## Short Reusable Lesson

- During EL sync startup, the node must not mark the current unsafe L2 head as safe or finalized just because sync progressed or a recovery path was taken; startup forkchoice should be derived from an older eligible L2 block based on L1-origin context, or from genuinely finalized state. Similar bugs appear when archive-extraction or file-materialization path code treats partially checked input as authoritative and lets it reach filesystem write outside the intended extraction or artifact directory. The reusable fix is to enforce path-confinement at the boundary and fail closed before state, privilege, or consensus-visible output changes.
