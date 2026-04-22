# Validation Card

## Metadata

- ID: `oasis-core-2019-07-24-oasis-core-cryptography-64cb06901`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-signer-authorization`

## What Confirmed The Issue

- Evidence 1: The fix replaced the old transaction-scheduler signature check with a call that verifies the signature against the active 'scheduler.KindTransactionScheduler' committee. It also introduced a generalized verifier interface so callers specify which committee kind a signature must belong to, and updated related storage call sites to use that interface.
- Evidence 2: The source finding states the invariant explicitly: A compute commitment's 'TxnSchedSig' must not only be cryptographically valid for the signed message; it must also be produced by a member of the active transaction scheduler committee for the relevant round/epoch.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
