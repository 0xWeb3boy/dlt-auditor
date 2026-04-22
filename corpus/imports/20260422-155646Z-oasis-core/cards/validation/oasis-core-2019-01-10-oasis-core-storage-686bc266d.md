# Validation Card

## Metadata

- ID: `oasis-core-2019-01-10-oasis-core-storage-686bc266d`
- Bug family: `authz_and_role_gates`
- Bug class: `improper-authorization-check`

## What Confirmed The Issue

- Evidence 1: The code now rejects unauthorized peers at the P2P boundary, routes committee batch handling through queueExternalBatch with a returned error path, and makes handleExternalBatch fail when the node is not in the expected state. These changes tighten validation and make rejection explicit.
- Evidence 2: The source finding states the invariant explicitly: Committee-related messages and external batches should only be accepted from authorized peers and only when the local worker is in the expected role and state for that path.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
