# Validation Card

## Metadata

- ID: `rippled-2026-04-03-rippled-access-control-c0ee81366`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-accounting-invariant`

## What Confirmed The Issue

- Evidence 1: Adds fixSecurity3_1_3-gated invariant logic in LoanBrokerInvariant.cpp.
- Evidence 2: Changes LoanBroker validation from a one-sided lower-bound check to a two-sided consistency check for non-delete transactions.

## What Could Have Invalidated It

- Compensating control 1: No proof of how invalid sfCoverAvailable state could be created by an attacker.
- Compensating control 2: No demonstrated authorization bypass, signer bug, or role-check failure.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-integrity, accounting-consistency
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No proof of how invalid sfCoverAvailable state could be created by an attacker.
- Caution 2: No demonstrated authorization bypass, signer bug, or role-check failure.
