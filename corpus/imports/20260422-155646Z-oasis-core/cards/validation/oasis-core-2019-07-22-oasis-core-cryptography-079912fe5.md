# Validation Card

## Metadata

- ID: `oasis-core-2019-07-22-oasis-core-cryptography-079912fe5`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-signer-authorization-check`

## What Confirmed The Issue

- Evidence 1: The fix introduced a helper on the epoch snapshot that checks whether each signature belongs to a current storage committee member, then wired that helper into the two shown compute-committee receipt paths so they reject non-member signers immediately.
- Evidence 2: The source finding states the invariant explicitly: Storage receipt signatures accepted by compute-committee code must come from members of the current storage committee for the active epoch; signatures from non-members must be rejected before batch acceptance or proposal assembly.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
