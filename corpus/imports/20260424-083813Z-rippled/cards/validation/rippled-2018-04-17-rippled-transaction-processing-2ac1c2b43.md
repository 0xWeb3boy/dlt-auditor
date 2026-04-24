# Validation Card

## Metadata

- ID: `rippled-2018-04-17-rippled-transaction-processing-2ac1c2b43`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `fee-accounting-invariant`

## What Confirmed The Issue

- Evidence 1: Commit message states a new invariant checker verifies fees are never higher than specified in the transaction.
- Evidence 2: ApplyContext API now documents and passes the actual charged fee into invariant checking.

## What Could Have Invalidated It

- Compensating control 1: No exploit path or attacker-controlled scenario is shown.
- Compensating control 2: No evidence proves users could previously force overcharging in an accepted ledger.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: fee-overcharge-prevention, ledger-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No exploit path or attacker-controlled scenario is shown.
- Caution 2: No evidence proves users could previously force overcharging in an accepted ledger.
