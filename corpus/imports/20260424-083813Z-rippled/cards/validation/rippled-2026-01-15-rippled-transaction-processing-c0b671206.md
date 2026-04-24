# Validation Card

## Metadata

- ID: `rippled-2026-01-15-rippled-transaction-processing-c0b671206`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rounding-accounting-yield-theft`

## What Confirmed The Issue

- Evidence 1: Commit body names "Yield Theft via Rounding Manipulation" and says the new test verifies no yield theft occurs.
- Evidence 2: LoanPay updates lending/vault repayment accounting involving rounded payments to the vault and broker.

## What Could Have Invalidated It

- Compensating control 1: Full regression test body is not provided.
- Compensating control 2: Exact STAmount.h and LendingHelpers.cpp changes are not shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: economic-value-theft, accounting-integrity
- Expected severity band: high

## False-Positive Cautions

- Caution 1: Full regression test body is not provided.
- Caution 2: Exact STAmount.h and LendingHelpers.cpp changes are not shown.
