# Validation Card

## Metadata

- ID: `nitro-2026-01-14-nitro-storage-9b7a73c97`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-gating`

## What Confirmed The Issue

- Evidence 1: The patch adds an explicit MEL validated-message-count gate before block validation creates new work, adjusts MEL validator progress tracking, and changes MEL state hash construction.
- Evidence 2: Add an explicit validation-progress gate at the boundary between MEL extraction validation and block validation, and align related progress-tracking and commitment construction code with that boundary.

## What Could Have Invalidated It

- Compensating control 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Compensating control 2: If the path is not enabled in production modes, downgrade similar patterns to hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Caution 2: Do not claim consensus impact without evidence that the bad state can escape local storage and influence validation or sequencing.
