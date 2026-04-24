# Validation Card

## Metadata

- ID: `rippled-2026-04-03-rippled-access-control-c979643d0`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `accounting-invariant`

## What Confirmed The Issue

- Evidence 1: Adds fixSecurity3_1_3-gated validation in ValidLoanBroker::finalize.
- Evidence 2: New invariant rejects sfCoverAvailable greater than the broker pseudo-account asset balance.

## What Could Have Invalidated It

- Compensating control 1: No advisory or security note is provided.
- Compensating control 2: No exploit sequence shows how an invalid LoanBroker state could be created.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: economic-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No advisory or security note is provided.
- Caution 2: No exploit sequence shows how an invalid LoanBroker state could be created.
