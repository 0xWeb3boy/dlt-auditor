# Root-Cause Card

## Metadata

- ID: `optimism-2025-05-17-optimism-p2p-networking-0b2e5f9cf7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `forkchoice-state-handling`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `path-confinement`

## Violated Invariant

- Invariant: While the execution layer is still syncing, the node should not report a newly inserted unsafe payload as safe or finalized, and startup event handling should not let an always-ready sync-complete signal dominate other pending state updates.

## Trust Boundary

- Boundary: artifact/archive input -> host filesystem

## Attack Surface

- Entrypoint type: archive-extraction or file-materialization path
- Sensitive sink: filesystem write outside the intended extraction or artifact directory

## Impact Pattern

- Primary impact: state-consistency
- Secondary impact: client-view-divergence

## Short Reusable Lesson

- While the execution layer is still syncing, the node should not report a newly inserted unsafe payload as safe or finalized, and startup event handling should not let an always-ready sync-complete signal dominate other pending state updates. Similar bugs appear when archive-extraction or file-materialization path code treats partially checked input as authoritative and lets it reach filesystem write outside the intended extraction or artifact directory. The reusable fix is to enforce path-confinement at the boundary and fail closed before state, privilege, or consensus-visible output changes.
