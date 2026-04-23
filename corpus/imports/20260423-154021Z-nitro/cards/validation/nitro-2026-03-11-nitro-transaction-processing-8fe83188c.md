# Validation Card

## Metadata

- ID: `nitro-2026-03-11-nitro-transaction-processing-8fe83188c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-integrity-check`

## What Confirmed The Issue

- Evidence 1: The patch appears to remove a MEL-specific gap where delayed-message sequencing could skip an accumulator continuity/reorg check and adds MEL support code needed to perform that check.
- Evidence 2: Move a previously conditional consistency check into the common execution path and add backend support methods so all modes can enforce the same invariant.

## What Could Have Invalidated It

- Compensating control 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Compensating control 2: If the path is not enabled in production modes, downgrade similar patterns to hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Caution 2: Do not claim consensus impact without evidence that the bad state can escape local storage and influence validation or sequencing.
