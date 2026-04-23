# Validation Card

## Metadata

- ID: `nitro-2026-01-05-nitro-transaction-processing-10aa51df2`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `incomplete-validation-recording`

## What Confirmed The Issue

- Evidence 1: The grounded change is that MEL extraction now records tx-indexed logs when consuming certain parent-chain logs, and aborts if that recording fails.
- Evidence 2: Make witness-recording mandatory at the point where relevant logs are consumed, and treat recording failure as a hard error.

## What Could Have Invalidated It

- Compensating control 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Compensating control 2: If the path is not enabled in production modes, downgrade similar patterns to hardening.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: If the subsystem later rebuilds the same state from finalized data before any decision point, similar cases may remain correctness-only.
- Caution 2: Do not claim consensus impact without evidence that the bad state can escape local storage and influence validation or sequencing.
