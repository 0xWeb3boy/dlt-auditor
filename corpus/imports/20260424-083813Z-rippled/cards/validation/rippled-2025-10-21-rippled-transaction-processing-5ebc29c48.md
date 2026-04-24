# Validation Card

## Metadata

- ID: `rippled-2025-10-21-rippled-transaction-processing-5ebc29c48`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `reserve-enforcement-bypass`

## What Confirmed The Issue

- Evidence 1: Adds an account reserve check before addEmptyHolding proceeds to trustCreate for a new holding object.
- Evidence 2: Patch is in VaultWithdraw transaction processing and shared ledger object creation code.

## What Could Have Invalidated It

- Compensating control 1: No reproducer or test contents showing an exploitable reserve bypass are provided.
- Compensating control 2: No evidence proves direct theft, unauthorized withdrawal, consensus divergence, or node compromise.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: state-accounting, resource-consumption
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No reproducer or test contents showing an exploitable reserve bypass are provided.
- Caution 2: No evidence proves direct theft, unauthorized withdrawal, consensus divergence, or node compromise.
