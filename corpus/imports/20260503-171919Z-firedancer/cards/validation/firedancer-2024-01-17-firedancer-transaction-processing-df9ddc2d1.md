# Validation Card

## Metadata

- ID: `firedancer-2024-01-17-firedancer-transaction-processing-df9ddc2d1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `signing-isolation-hardening`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says security: add remote signing tile for shreds.
- Evidence 2: Shred tile topology is changed to require SIGN_TO_SHRED input and SHRED_TO_SIGN output links.

## What Could Have Invalidated It

- Compensating control 1: No evidence that the previous shred signing path accepted attacker-controlled signing requests.
- Compensating control 2: No evidence of arbitrary payload signing before the patch.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No evidence that the previous shred signing path accepted attacker-controlled signing requests.
- Caution 2: No evidence of arbitrary payload signing before the patch.
