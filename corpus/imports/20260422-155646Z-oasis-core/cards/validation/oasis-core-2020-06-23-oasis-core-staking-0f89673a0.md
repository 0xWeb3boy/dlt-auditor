# Validation Card

## Metadata

- ID: `oasis-core-2020-06-23-oasis-core-staking-0f89673a0`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-update-validation`

## What Confirmed The Issue

- Evidence 1: 'registerNode' now calls 'registry.VerifyNodeUpdate(...)' whenever a prior node record exists, including when that record is expired, before accepting the new descriptor and writing it to state. The tests were adjusted to keep prior registrations around for later update-oriented cases.
- Evidence 2: The source finding states the invariant explicitly: A registration must not overwrite a previously stored node record without passing the registry's node-update verification, even if the stored record is expired.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
