# Root-Cause Card

## Metadata

- ID: `oasis-core-2019-10-11-oasis-core-storage-82a0d8ee2`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `state-integrity-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `state-coordinate-consistency`

## Violated Invariant

- Invariant: During remote subtree merge and dereference, cache admission must not evict the node currently being dereferenced; if capacity prevents preserving that pointer, the operation should stop or fail rather than continue with inconsistent in-memory tree state.

## Trust Boundary

- Boundary: `peer->node`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `security-sensitive consensus or registry state`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- During remote subtree merge and dereference, cache admission must not evict the node currently being dereferenced; if capacity prevents preserving that pointer, the operation should stop or fail rather than continue with inconsistent in-memory tree state. In this pattern, eviction and commit logic in the remote merge path did not account for the pointer currently being dereferenced, so cache pressure could remove that active node during merge. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
