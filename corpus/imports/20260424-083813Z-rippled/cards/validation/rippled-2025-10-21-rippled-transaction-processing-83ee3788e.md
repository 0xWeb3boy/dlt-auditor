# Validation Card

## Metadata

- ID: `rippled-2025-10-21-rippled-transaction-processing-83ee3788e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-reserve-check`

## What Confirmed The Issue

- Evidence 1: Commit message explicitly says VaultWithdraw should enforce reserve before creating a new object.
- Evidence 2: View.cpp adds an owner reserve check before trustCreate/addEmptyHolding proceeds.

## What Could Have Invalidated It

- Compensating control 1: No exploit scenario or proof of abuse impact is provided.
- Compensating control 2: No evidence shows direct fund theft, authorization bypass, consensus failure, or memory safety impact.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-invariant-bypass, economic-policy-bypass
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No exploit scenario or proof of abuse impact is provided.
- Caution 2: No evidence shows direct fund theft, authorization bypass, consensus failure, or memory safety impact.
