# Validation Card

## Metadata

- ID: `base-2026-03-22-base-consensus-424476a9d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- Evidence 1: `start_sequencer` previously ignored the supplied `unsafe_head` for activation and set `is_active = true` unconditionally after earlier checks.
- Evidence 2: The new code fetches the engine unsafe head and returns an error if the fetch fails, adding a stricter precondition before sequencer activation.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: the patch hardens a consensus-sensitive activation path by enforcing engine-state validation before starting the sequencer.
- Compensating control 2: Supported claim: the patch removes a risky condition where sequencing could begin while the engine unsafe head is still uninitialized.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: the patch hardens a consensus-sensitive activation path by enforcing engine-state validation before starting the sequencer.
- Caution 2: Supported claim: the patch removes a risky condition where sequencing could begin while the engine unsafe head is still uninitialized.
