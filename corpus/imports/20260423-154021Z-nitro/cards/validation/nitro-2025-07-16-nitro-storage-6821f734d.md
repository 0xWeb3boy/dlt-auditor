# Validation Card

## Metadata

- ID: `nitro-2025-07-16-nitro-storage-6821f734d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `state-validation-hardening`

## What Confirmed The Issue

- Evidence 1: The evidence supports a consensus-sensitive correctness hardening change in MEL state handling, not a confirmed vulnerability fix.
- Evidence 2: Re-derive cached validation state from canonical persisted data before use, and make pruning and head-state updates follow explicit safety conditions.

## What Could Have Invalidated It

- Compensating control 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Compensating control 2: If the path is not enabled in production modes, downgrade similar patterns to hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Caution 2: Do not claim consensus impact without evidence that the bad state can escape local storage and influence validation or sequencing.
