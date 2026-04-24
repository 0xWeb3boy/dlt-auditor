# Validation Card

## Metadata

- ID: `rippled-2025-05-05-rippled-transaction-processing-9a8660241`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-accounting-invariant-hardening`

## What Confirmed The Issue

- Evidence 1: LoanManage now checks sfLossUnrealized before subtracting principal plus interest and returns tefBAD_LEDGER on insufficient value.
- Evidence 2: LoanManage now checks sfAssetsTotal before reducing it by the default amount and returns tefBAD_LEDGER on insufficient value.

## What Could Have Invalidated It

- Compensating control 1: No demonstrated attacker-controlled transaction sequence is provided.
- Compensating control 2: No proof of asset loss, unauthorized transfer, consensus failure, or node crash is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-integrity, state-consistency
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No demonstrated attacker-controlled transaction sequence is provided.
- Caution 2: No proof of asset loss, unauthorized transfer, consensus failure, or node crash is shown.
