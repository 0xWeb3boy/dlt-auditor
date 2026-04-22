# Validation Card

## Metadata

- ID: `oasis-core-2020-12-01-oasis-core-storage-af0555775`
- Bug family: `authz_and_role_gates`
- Bug class: `validation-bypass`

## What Confirmed The Issue

- Evidence 1: The patch removed the 'disableCheckTx' special case from the ABCI mux 'CheckTx' path, removed the related debug transaction-expiry state, removed test-runner support for enabling the option, and updated the oversized transaction workload to stop tolerating behavior caused by skipped 'CheckTx'.
- Evidence 2: The source finding states the invariant explicitly: Transactions submitted through the Tendermint/ABCI mempool path should undergo normal 'CheckTx' admission validation instead of being accepted via a local bypass mode.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
