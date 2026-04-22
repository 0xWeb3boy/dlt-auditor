# Root-Cause Card

## Metadata

- ID: `oasis-core-2023-10-02-oasis-core-consensus-87f19bb1e`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-role-scoped-enforcement`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `role-scoping`

## Violated Invariant

- Invariant: Worker liveness enforcement should be driven only by committee members that have worker-role liveness obligations. Non-worker roles, including backup workers, should not contribute worker liveness credit or have worker liveness penalties applied through mixed per-node accounting.

## Trust Boundary

- Boundary: `validator->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `validator penalty state`

## Impact Pattern

- Primary impact: `integrity`
- Secondary impact: `availability`

## Short Reusable Lesson

- Worker liveness enforcement should be driven only by committee members that have worker-role liveness obligations. Non-worker roles, including backup workers, should not contribute worker liveness credit or have worker liveness penalties applied through mixed per-node accounting. In this pattern, liveness accounting and enforcement were scoped too broadly across committee roles for the same node. That mixed worker obligations with backup-worker handling instead of isolating worker liveness evaluation to worker-role entries. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
