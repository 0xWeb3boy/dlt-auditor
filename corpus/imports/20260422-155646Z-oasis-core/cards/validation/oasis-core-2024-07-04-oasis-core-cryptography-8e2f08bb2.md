# Validation Card

## Metadata

- ID: `oasis-core-2024-07-04-oasis-core-cryptography-8e2f08bb2`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: The patch tightens worker-side authorization for CHURP key-share queries by consulting runtime descriptor information, and it adds consensus-side validation so 'MayQuery' cannot be set before the feature release that supports it.
- Evidence 2: The source finding states the invariant explicitly: CHURP key-share query handling should apply explicit authorization rules tied to runtime/policy context, and consensus should not admit 'MayQuery' policy state before the protocol version that defines and supports it.

## What Could Have Invalidated It

- Compensating control 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Compensating control 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `high_or_medium`

## False-Positive Cautions

- Caution 1: Not a match if every route to the sink already passes through one canonical authorization helper with the same role and policy checks.
- Caution 2: Not a match if the diff only renames roles or improves logging without changing who can reach the action.
