# Validation Card

## Metadata

- ID: `rippled-2026-04-22-rippled-transaction-processing-2794a7503`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `invariant-check-state-overwrite`

## What Confirmed The Issue

- Evidence 1: InvariantCheck.cpp changes violation state from assignment to OR accumulation for XRP trust-line detection.
- Evidence 2: InvariantCheck.cpp applies the same latching pattern to deep-freeze-without-freeze detection.

## What Could Have Invalidated It

- Compensating control 1: No evidence that an attacker can create the prohibited ledger states.
- Compensating control 2: No end-to-end exploit path is shown.

## Severity Guidance

- Expected impact band: hardening-or-limited-security-impact: invariant-detection-bypass
- Expected severity band: medium_or_high

## False-Positive Cautions

- Caution 1: No evidence that an attacker can create the prohibited ledger states.
- Caution 2: No end-to-end exploit path is shown.
