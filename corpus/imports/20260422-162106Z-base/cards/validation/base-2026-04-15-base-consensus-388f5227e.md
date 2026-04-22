# Validation Card

## Metadata

- ID: `base-2026-04-15-base-consensus-388f5227e`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validation-coverage-gap`

## What Confirmed The Issue

- Evidence 1: The scanner changed from watermark-based incremental discovery to full lookback rescanning so later on-chain proof changes are always reconsidered.
- Evidence 2: A previously skipped dual-proof state `(true, true, 0)` now becomes `Some(GameCategory::InvalidDualProposal)` and is sent for validation.

## What Could Have Invalidated It

- Compensating control 1: This supports a security-sensitive detection and coverage hardening change, not a proven exploitable vulnerability.
- Compensating control 2: The evidence shows missed validation/classification risk in the challenger, not that validator or submitter logic was itself incorrect.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: This supports a security-sensitive detection and coverage hardening change, not a proven exploitable vulnerability.
- Caution 2: The evidence shows missed validation/classification risk in the challenger, not that validator or submitter logic was itself incorrect.
