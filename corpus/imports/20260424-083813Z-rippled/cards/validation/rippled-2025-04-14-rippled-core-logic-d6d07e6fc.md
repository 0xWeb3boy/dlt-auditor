# Validation Card

## Metadata

- ID: `rippled-2025-04-14-rippled-core-logic-d6d07e6fc`
- Bug family: `authz_and_role_gates`
- Bug class: `authorization-correctness`

## What Confirmed The Issue

- Evidence 1: Commit subject is "Fix authorization issues".
- Evidence 2: VaultDeposit private-vault path now reads share MPTokenIssuance and DomainID metadata before authorization handling.

## What Could Have Invalidated It

- Compensating control 1: No complete before/after authorization branch is shown.
- Compensating control 2: No regression test details are provided in the evidence.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: authorization-enforcement
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No complete before/after authorization branch is shown.
- Caution 2: No regression test details are provided in the evidence.
