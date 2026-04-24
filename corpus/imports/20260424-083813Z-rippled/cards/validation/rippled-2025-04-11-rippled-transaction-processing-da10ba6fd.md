# Validation Card

## Metadata

- ID: `rippled-2025-04-11-rippled-transaction-processing-da10ba6fd`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `ledger-state-integrity`

## What Confirmed The Issue

- Evidence 1: LoanBrokerDelete::doApply changed from directly erasing brokerPseudoSLE to checking sfBalance before deletion.
- Evidence 2: LoanBrokerDelete::doApply now returns tecHAS_OBLIGATIONS if the pseudo-account still has a nonzero balance.

## What Could Have Invalidated It

- Compensating control 1: No evidence shows an attacker could trigger the stale-obligation condition on a live network.
- Compensating control 2: No evidence proves loss of funds, unauthorized asset movement, or consensus impact.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: ledger-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No evidence shows an attacker could trigger the stale-obligation condition on a live network.
- Caution 2: No evidence proves loss of funds, unauthorized asset movement, or consensus impact.
