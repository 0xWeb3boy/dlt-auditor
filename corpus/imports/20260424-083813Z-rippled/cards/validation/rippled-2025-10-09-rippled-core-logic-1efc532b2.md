# Validation Card

## Metadata

- ID: `rippled-2025-10-09-rippled-core-logic-1efc532b2`
- Bug family: `authz_and_role_gates`
- Bug class: `receiver-authorization-hardening`

## What Confirmed The Issue

- Evidence 1: LoanPay now calls requireAuth with StrongAuth when totalPaidToVault is nonzero before value is paid to the vault pseudo-account.
- Evidence 2: Commit metadata explicitly says LoanPay will check auth for receivers and account for deep-frozen broker-owner fee handling.

## What Could Have Invalidated It

- Compensating control 1: No exploit scenario or attacker-controlled transaction sequence is provided.
- Compensating control 2: No evidence shows that the old behavior was reachable in a released configuration.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: authorization-policy-enforcement, asset-transfer-eligibility
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No exploit scenario or attacker-controlled transaction sequence is provided.
- Caution 2: No evidence shows that the old behavior was reachable in a released configuration.
