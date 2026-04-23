# Validation Card

## Metadata

- ID: `nitro-2025-07-07-nitro-storage-a1b99c526`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `verification-state-retention`

## What Confirmed The Issue

- Evidence 1: The patch is well supported as a correctness/state-handling change in MEL delayed-message tracking.
- Evidence 2: Replace implicit or lazily created tracking state with an explicitly initialized backlog, and tie retention/cleanup to finalized state rather than local assumptions.

## What Could Have Invalidated It

- Compensating control 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Compensating control 2: If the path is not enabled in production modes, downgrade similar patterns to hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Caution 2: Do not claim consensus impact without evidence that the bad state can escape local storage and influence validation or sequencing.
