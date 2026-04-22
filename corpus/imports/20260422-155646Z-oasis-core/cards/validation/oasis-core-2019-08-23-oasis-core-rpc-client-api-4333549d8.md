# Validation Card

## Metadata

- ID: `oasis-core-2019-08-23-oasis-core-rpc-client-api-4333549d8`
- Bug family: `authz_and_role_gates`
- Bug class: `missing-authentication`

## What Confirmed The Issue

- Evidence 1: The fix adds a mandatory authenticator call in the VerifyEvidence handler using the request signer key and decoded evidence, and aborts the RPC when that validation fails. Related proxy changes centralize endpoint/authenticator creation and make the development skip-auth mode explicit rather than leaving enforcement absent in the normal handler path.
- Evidence 2: The source finding states the invariant explicitly: The IAS VerifyEvidence RPC must not accept a request solely because its SignedEvidence blob parses; it must also enforce the configured attestation policy for the caller and decoded evidence before proceeding.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
