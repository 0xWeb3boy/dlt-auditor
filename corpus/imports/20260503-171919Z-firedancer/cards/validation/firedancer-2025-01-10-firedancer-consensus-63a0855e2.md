# Validation Card

## Metadata

- ID: `firedancer-2025-01-10-firedancer-consensus-63a0855e2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-state-persistence`

## What Confirmed The Issue

- Evidence 1: Nonce authorization no longer returns immediately; it records the nonce account index for later finalization.
- Evidence 2: The new comment says the nonce account must be modified and hashed even if transaction execution fails.

## What Could Have Invalidated It

- Compensating control 1: No concrete attacker workflow or replay transaction is shown.
- Compensating control 2: No failing test output or regression case is provided in the input.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No concrete attacker workflow or replay transaction is shown.
- Caution 2: No failing test output or regression case is provided in the input.
