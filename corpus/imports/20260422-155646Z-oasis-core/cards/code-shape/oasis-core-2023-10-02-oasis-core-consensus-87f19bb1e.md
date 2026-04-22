# Code-Shape Card

## Metadata

- ID: `oasis-core-2023-10-02-oasis-core-consensus-87f19bb1e`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-role-scoped-enforcement`

## Code Shape Summary

- Short description of what the buggy code looked like: Liveness accounting and enforcement were scoped too broadly across committee roles for the same node. That mixed worker obligations with backup-worker handling instead of isolating worker liveness evaluation to worker-role entries.

## Search Motifs

- Motif 1: valid request path missing a secondary role or policy gate
- Motif 2: authorization derived from one scope but sink executes in another
- Motif 3: shared helper returns success before role-specific enforcement

## Typical Asymmetry

- What was checked in one path but missing in another: Cryptographic validity or basic parsing succeeded, but the path still lacked the role, authorization, or policy check needed for the sensitive action.

## Patch Pattern

- What the fix changed structurally: The patch removed the old per-node multi-role aggregation approach in 'liveness.go', changed liveness enforcement to a worker-only loop, and updated slashing/status writes to use the current member public key. In 'finalization.go', it deleted the backup-worker live-round credit branch. In 'liveness_test.go', it added coverage that backup-worker status must not change worker fault accounting.

## False Match Warnings

- What looks similar but is often not a bug: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
