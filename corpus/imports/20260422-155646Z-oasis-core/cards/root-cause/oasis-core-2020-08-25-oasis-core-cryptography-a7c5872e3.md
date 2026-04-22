# Root-Cause Card

## Metadata

- ID: `oasis-core-2020-08-25-oasis-core-cryptography-a7c5872e3`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-timeout-state`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `timeout-state-consistency`

## Violated Invariant

- Invariant: Round-timeout state must stay consistent with the active executor round; when an empty block ends or transitions a round, any previously scheduled timeout for that round should be cleared before commitments are reset and the new state proceeds.

## Trust Boundary

- Boundary: `committee-member->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `round timeout scheduler state`

## Impact Pattern

- Primary impact: `state-consistency`
- Secondary impact: `liveness-disruption`

## Short Reusable Lesson

- Round-timeout state must stay consistent with the active executor round; when an empty block ends or transitions a round, any previously scheduled timeout for that round should be cleared before commitments are reset and the new state proceeds. In this pattern, a round-transition helper ('emitEmptyBlock') did not perform the same timeout-state cleanup that the finalization path already treated as part of normal round lifecycle management. As a result, a previously armed timeout could remain in persistent state when commitments were reset via the empty-block path. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
