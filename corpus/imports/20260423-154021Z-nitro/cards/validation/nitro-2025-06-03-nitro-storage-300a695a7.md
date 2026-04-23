# Validation Card

## Metadata

- ID: `nitro-2025-06-03-nitro-storage-300a695a7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `finality-boundary-handling`

## What Confirmed The Issue

- Evidence 1: The patch changes MEL startup and state-recovery logic to use the finalized parent-chain block when initializing delayed-message tracking.
- Evidence 2: Thread an explicit finalized-boundary parameter through recovery code, and gate state initialization and trimming on finality rather than read-progress alone.

## What Could Have Invalidated It

- Compensating control 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Compensating control 2: If the path is not enabled in production modes, downgrade similar patterns to hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Caution 2: Do not claim consensus impact without evidence that the bad state can escape local storage and influence validation or sequencing.
