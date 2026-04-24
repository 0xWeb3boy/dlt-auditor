# Validation Card

## Metadata

- ID: `rippled-2013-01-19-rippled-transaction-processing-308ca21b9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reserve-enforcement-bypass`

## What Confirmed The Issue

- Evidence 1: WalletAdd previously rejected only when source balance was below the sent amount.
- Evidence 2: WalletAdd now also accounts for the source account reserve derived from owner count and ledger reserve.

## What Could Have Invalidated It

- Compensating control 1: No exploit scenario or attacker-controlled sequence is shown.
- Compensating control 2: No evidence shows theft, double spend, value creation, or consensus divergence.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: state-accounting, economic-policy-bypass
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No exploit scenario or attacker-controlled sequence is shown.
- Caution 2: No evidence shows theft, double spend, value creation, or consensus divergence.
