# Validation Card

## Metadata

- ID: `base-2025-12-29-base-storage-d9350fcc9`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-precondition-check`

## What Confirmed The Issue

- Evidence 1: `proposer.rs` adds an explicit precondition check against `anchor_state_registry.respectedGameType()` immediately before game creation.
- Evidence 2: On mismatch, the proposer logs a warning and returns early, skipping the side-effecting create path.

## What Could Have Invalidated It

- Compensating control 1: The patch proves a missing runtime validation was added before creating dispute games.
- Compensating control 2: The patch supports classifying the change as security hardening in a sensitive blockchain path.

## Severity Guidance

- Expected impact band: `trust_or_policy_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The patch proves a missing runtime validation was added before creating dispute games.
- Caution 2: The patch supports classifying the change as security hardening in a sensitive blockchain path.
