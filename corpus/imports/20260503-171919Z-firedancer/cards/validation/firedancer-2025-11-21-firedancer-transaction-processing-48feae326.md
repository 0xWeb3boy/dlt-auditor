# Validation Card

## Metadata

- ID: `firedancer-2025-11-21-firedancer-transaction-processing-48feae326`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `out-of-bounds-read`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says "gui: fix cJSON_Parse overrun".
- Evidence 2: Parser bounds check changes from CHECK_LEFT(json_str_sz) to CHECK_LEFT(json_str_sz+1UL).

## What Could Have Invalidated It

- Compensating control 1: No crash trace, sanitizer report, PoC, or exploit scenario is provided.
- Compensating control 2: No evidence that the overread crosses a sensitive boundary or leaks data.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No crash trace, sanitizer report, PoC, or exploit scenario is provided.
- Caution 2: No evidence that the overread crosses a sensitive boundary or leaks data.
