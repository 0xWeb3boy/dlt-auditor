# Validation Card

## Metadata

- ID: `rippled-2025-11-16-rippled-core-logic-248d267f2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `numeric-validation`

## What Confirmed The Issue

- Evidence 1: VaultCreate rejects integral sfAssetsMaximum values that are not valid under Number::compatible.
- Evidence 2: VaultSet applies the same Number::compatible validation when updating sfAssetsMaximum.

## What Could Have Invalidated It

- Compensating control 1: No exploit path is shown.
- Compensating control 2: No demonstrated funds loss, unauthorized action, or privilege bypass is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: state-integrity, consensus-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No exploit path is shown.
- Caution 2: No demonstrated funds loss, unauthorized action, or privilege bypass is shown.
