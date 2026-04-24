# Validation Card

## Metadata

- ID: `rippled-2025-04-07-rippled-access-control-f839049de`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-recursion-boundary`

## What Confirmed The Issue

- Evidence 1: requireAuth recursion guard changed from depth > maxFreezeCheckDepth to depth >= maxFreezeCheckDepth.
- Evidence 2: VaultCreate now checks MPT assets through requireAuth specifically to detect excessive vault-share recursion returning tecKILLED.

## What Could Have Invalidated It

- Compensating control 1: No exploit scenario is shown.
- Compensating control 2: No proof that the old off-by-one caused denial of service, authorization bypass, or incorrect ledger acceptance.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: authorization-hardening, availability-hardening
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No exploit scenario is shown.
- Caution 2: No proof that the old off-by-one caused denial of service, authorization bypass, or incorrect ledger acceptance.
