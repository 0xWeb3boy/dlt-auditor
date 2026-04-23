# Validation Card

## Metadata

- ID: `nitro-2025-06-02-nitro-storage-b3bbf4e7d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-validation`

## What Confirmed The Issue

- Evidence 1: The provided evidence supports that this patch implements previously missing delayed-message accumulation and accumulator checks in native-mode MEL.
- Evidence 2: Replace placeholder state/update and always-success validation code with explicit accumulator reconstruction, indexed context tracking, and real checks.

## What Could Have Invalidated It

- Compensating control 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Compensating control 2: If the path is not enabled in production modes, downgrade similar patterns to hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Caution 2: Do not claim consensus impact without evidence that the bad state can escape local storage and influence validation or sequencing.
