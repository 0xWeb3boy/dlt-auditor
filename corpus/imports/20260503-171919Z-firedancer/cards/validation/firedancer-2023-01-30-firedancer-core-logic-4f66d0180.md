# Validation Card

## Metadata

- ID: `firedancer-2023-01-30-firedancer-core-logic-4f66d0180`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `malformed-archive-metadata-parsing`

## What Confirmed The Issue

- Evidence 1: Commit body explicitly says security issues were eliminated in AR metadata parsing.
- Evidence 2: Commit body identifies concrete malformed-input cases: all-whitespace fields, strtol running off the end, negative sizes, and infinite archive iterator loops.

## What Could Have Invalidated It

- Compensating control 1: No full parser implementation diff is provided showing exact bounds checks or rejection logic.
- Compensating control 2: No concrete remote or attacker-controlled input path is established.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No full parser implementation diff is provided showing exact bounds checks or rejection logic.
- Caution 2: No concrete remote or attacker-controlled input path is established.
