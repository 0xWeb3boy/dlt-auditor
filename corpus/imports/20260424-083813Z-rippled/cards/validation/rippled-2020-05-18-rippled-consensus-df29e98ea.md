# Validation Card

## Metadata

- ID: `rippled-2020-05-18-rippled-consensus-df29e98ea`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-threshold-rounding`

## What Confirmed The Issue

- Evidence 1: Commit message states amendment ballot counting could reach majority with slightly less than 80% support.
- Evidence 2: Changed AmendmentSet construction now receives consensus rules and the validation set.

## What Could Have Invalidated It

- Compensating control 1: No evidence that an amendment actually activated incorrectly.
- Compensating control 2: No evidence of a realized fork or consensus split from the rounding flaw.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: protocol-governance-integrity
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No evidence that an amendment actually activated incorrectly.
- Caution 2: No evidence of a realized fork or consensus split from the rounding flaw.
