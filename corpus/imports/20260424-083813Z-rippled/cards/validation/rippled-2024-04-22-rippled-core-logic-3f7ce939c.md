# Validation Card

## Metadata

- ID: `rippled-2024-04-22-rippled-core-logic-3f7ce939c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `amm-rounding-invariant-hardening`

## What Confirmed The Issue

- Evidence 1: Commit body identifies an AMM swap invariant: new_balance_1 * new_balance_2 >= old_balance_1 * old_balance_2.
- Evidence 2: Commit body says rounding could sometimes violate that invariant.

## What Could Have Invalidated It

- Compensating control 1: The supplied hunks do not show the actual AMM rounding arithmetic change.
- Compensating control 2: No transaction-level exploit, proof of profit, or drain scenario is provided.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: protocol-accounting-integrity, economic-invariant-preservation
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: The supplied hunks do not show the actual AMM rounding arithmetic change.
- Caution 2: No transaction-level exploit, proof of profit, or drain scenario is provided.
