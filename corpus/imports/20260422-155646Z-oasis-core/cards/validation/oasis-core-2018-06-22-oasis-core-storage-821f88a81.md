# Validation Card

## Metadata

- ID: `oasis-core-2018-06-22-oasis-core-storage-821f88a81`
- Bug family: `authz_and_role_gates`
- Bug class: `consensus-role-accounting`

## What Confirmed The Issue

- Evidence 1: The patch first changes the verification-side code to locate the specific committee entry for the signing key. It then changes the aggregation handlers to branch on sender role and use role-specific queueing and thresholds instead of a single generic queue.
- Evidence 2: The source finding states the invariant explicitly: Aggregation should account for commitments and reveals according to the actual committee member role associated with the signing key, rather than treating all allowed signers through one undifferentiated path.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
