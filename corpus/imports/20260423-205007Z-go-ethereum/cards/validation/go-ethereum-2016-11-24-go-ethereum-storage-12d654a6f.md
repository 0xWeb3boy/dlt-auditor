# Validation Card

## Metadata

- ID: `go-ethereum-2016-11-24-go-ethereum-storage-12d654a6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-revert-bug`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says a consensus issue was fixed.
- Evidence 2: Commit body says the change was needed to remain in sync with the current longest chain.

## What Could Have Invalidated It

- Compensating control 1: Valid claim: consensus-relevant state handling for touched empty accounts was corrected or made client-compatible.
- Compensating control 2: Valid claim: Snapshot/Revert behavior for touch state became explicitly journaled and reversible.

## Severity Guidance

- Expected impact band: high
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Valid claim: consensus-relevant state handling for touched empty accounts was corrected or made client-compatible.
- Caution 2: Valid claim: Snapshot/Revert behavior for touch state became explicitly journaled and reversible.
