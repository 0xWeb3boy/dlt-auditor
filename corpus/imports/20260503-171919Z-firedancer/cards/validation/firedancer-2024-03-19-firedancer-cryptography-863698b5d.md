# Validation Card

## Metadata

- ID: `firedancer-2024-03-19-firedancer-cryptography-863698b5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-liveness-failure`

## What Confirmed The Issue

- Evidence 1: Patch changes PoH leader-transition logic in validator code.
- Evidence 2: Commit describes infinite forking after a previous leader skipped slots.

## What Could Have Invalidated It

- Compensating control 1: No demonstrated remote exploit path beyond skipped-slot conditions.
- Compensating control 2: No evidence of transaction forgery, signature bypass, or replay attack.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No demonstrated remote exploit path beyond skipped-slot conditions.
- Caution 2: No evidence of transaction forgery, signature bypass, or replay attack.
