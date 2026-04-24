# Validation Card

## Metadata

- ID: `rippled-2025-09-10-rippled-transaction-processing-61d628d65`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: DelegateSet preflight now rejects non-delegatable permission values when fixDelegateV1_1 is enabled.
- Evidence 2: Permission::isDelegatable now maps permission values through permissionToTxType and rejects unknown transaction permissions under the amendment.

## What Could Have Invalidated It

- Compensating control 1: No exploit transaction or demonstrated attack path is provided.
- Compensating control 2: No concrete funds theft, consensus failure, or remote compromise impact is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: privilege-misuse
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No exploit transaction or demonstrated attack path is provided.
- Caution 2: No concrete funds theft, consensus failure, or remote compromise impact is shown.
