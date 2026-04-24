# Validation Card

## Metadata

- ID: `rippled-2026-04-02-rippled-access-control-111edef28`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-accounting-invariant`

## What Confirmed The Issue

- Evidence 1: InvariantCheck.cpp adds a fixSecurity3_1_3-gated upper-bound check for sfCoverAvailable against pseudoBalance.
- Evidence 2: The check rejects non-delete LoanBroker state where recorded cover exceeds actual pseudo-account holdings.

## What Could Have Invalidated It

- Compensating control 1: No transaction sequence is shown that can create an excessive sfCoverAvailable value before the fix.
- Compensating control 2: No exploit path, funds theft, signature bypass, or privilege escalation is demonstrated.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-integrity, protocol-accounting-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No transaction sequence is shown that can create an excessive sfCoverAvailable value before the fix.
- Caution 2: No exploit path, funds theft, signature bypass, or privilege escalation is demonstrated.
