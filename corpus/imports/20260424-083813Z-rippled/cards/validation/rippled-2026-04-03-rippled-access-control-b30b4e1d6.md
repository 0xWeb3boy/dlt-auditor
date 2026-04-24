# Validation Card

## Metadata

- ID: `rippled-2026-04-03-rippled-access-control-b30b4e1d6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `protocol-accounting-invariant`

## What Confirmed The Issue

- Evidence 1: LoanBrokerInvariant.cpp adds fixSecurity3_1_3-gated validation for sfCoverAvailable greater than pseudoBalance.
- Evidence 2: The new check compares recorded LoanBroker cover against actual pseudo-account holdings for the vault asset.

## What Could Have Invalidated It

- Compensating control 1: No concrete transaction sequence is shown that creates sfCoverAvailable greater than pseudoBalance.
- Compensating control 2: No advisory, issue text, or vulnerability description is supplied.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-state-integrity, economic-accounting-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No concrete transaction sequence is shown that creates sfCoverAvailable greater than pseudoBalance.
- Caution 2: No advisory, issue text, or vulnerability description is supplied.
