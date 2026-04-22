# Root-Cause Card

## Metadata

- ID: `oasis-core-2024-03-16-oasis-core-storage-68133d1f3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `protocol-state-confusion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: CHURP request validation, persisted handoff-specific dealer state, and submission scheduling should all use the same canonical handoff epoch identifier. The diff supports that consistency invariant, but does not by itself establish a concrete security failure from the prior 'round'-based behavior.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `handoff-scoped key-generation state`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- CHURP request validation, persisted handoff-specific dealer state, and submission scheduling should all use the same canonical handoff epoch identifier. The diff supports that consistency invariant, but does not by itself establish a concrete security failure from the prior 'round'-based behavior. In this pattern, inconsistent use of two related state coordinates ('round' versus 'handoff') across the CHURP subsystem. The evidence shows that some paths were bound to 'round' even though surrounding logic and comments indicate the operation is scoped to a handoff epoch. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
