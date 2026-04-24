# Validation Card

## Metadata

- ID: `rippled-2025-03-11-rippled-core-logic-3715d7e2e`
- Bug family: `authz_and_role_gates`
- Bug class: `access-control`

## What Confirmed The Issue

- Evidence 1: VaultDeposit now checks the private-vault flag with a bitwise test instead of exact equality, preventing private handling from being skipped when other flags are set.
- Evidence 2: VaultDeposit explicitly applies the private-vault authorization path to non-owner accounts while exempting the vault owner.

## What Could Have Invalidated It

- Compensating control 1: No advisory, issue discussion, or exploit report is provided.
- Compensating control 2: Tests are mentioned but their assertions are not included in the supplied evidence.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: privilege-misuse
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No advisory, issue discussion, or exploit report is provided.
- Caution 2: Tests are mentioned but their assertions are not included in the supplied evidence.
