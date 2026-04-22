# Validation Card

## Metadata

- ID: `oasis-core-2023-10-02-oasis-core-consensus-87f19bb1e`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-role-scoped-enforcement`

## What Confirmed The Issue

- Evidence 1: The patch removed the old per-node multi-role aggregation approach in 'liveness.go', changed liveness enforcement to a worker-only loop, and updated slashing/status writes to use the current member public key. In 'finalization.go', it deleted the backup-worker live-round credit branch. In 'liveness_test.go', it added coverage that backup-worker status must not change worker fault accounting.
- Evidence 2: The source finding states the invariant explicitly: Worker liveness enforcement should be driven only by committee members that have worker-role liveness obligations. Non-worker roles, including backup workers, should not contribute worker liveness credit or have worker liveness penalties applied through mixed per-node accounting.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `availability_or_resource_exhaustion`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
