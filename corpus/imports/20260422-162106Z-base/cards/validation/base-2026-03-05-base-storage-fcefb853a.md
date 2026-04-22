# Validation Card

## Metadata

- ID: `base-2026-03-05-base-storage-fcefb853a`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `insufficient-input-validation`

## What Confirmed The Issue

- Evidence 1: The commit body explicitly says `fix(challenger): harden OutputValidator against adversarial inputs`.
- Evidence 2: The described pre-fix behavior includes a fail-open case where too-few intermediate roots could cause remaining checkpoints to be skipped while validation still reported success.

## What Could Have Invalidated It

- Compensating control 1: Treat this as challenger-side validation hardening, not a confirmed consensus-break or fund-loss bug.
- Compensating control 2: Do not claim a proven exploitable shipped vulnerability from the supplied snippets alone.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Treat this as challenger-side validation hardening, not a confirmed consensus-break or fund-loss bug.
- Caution 2: Do not claim a proven exploitable shipped vulnerability from the supplied snippets alone.
