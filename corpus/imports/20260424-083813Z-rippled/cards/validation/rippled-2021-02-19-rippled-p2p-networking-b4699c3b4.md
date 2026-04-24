# Validation Card

## Metadata

- ID: `rippled-2021-02-19-rippled-p2p-networking-b4699c3b4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-misbehavior-detection-gap`

## What Confirmed The Issue

- Evidence 1: Commit message explicitly says the Byzantine validation detector now receives all validations, not only UNL validators.
- Evidence 2: Validations.h adds detection of same-sequence, same-ledger validations with different sign times as ValStatus::conflicting, with comments tying the pattern to possible Byzantine...

## What Could Have Invalidated It

- Compensating control 1: No evidence that prior behavior allowed invalid validations to affect consensus decisions.
- Compensating control 2: No demonstrated exploit path, remote attacker capability, fund loss, or ledger safety violation.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: validator-misbehavior-detection
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: No evidence that prior behavior allowed invalid validations to affect consensus decisions.
- Caution 2: No demonstrated exploit path, remote attacker capability, fund loss, or ledger safety violation.
