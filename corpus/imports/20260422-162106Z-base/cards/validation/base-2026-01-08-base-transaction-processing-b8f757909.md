# Validation Card

## Metadata

- ID: `base-2026-01-08-base-transaction-processing-b8f757909`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `deadline-enforcement`

## What Confirmed The Issue

- Evidence 1: `sync_state` drives challenge/resolve decisions for dispute games in the fault-proof challenger.
- Evidence 2: The patch replaces a proposal-status-gated game-over check with an unconditional deadline check.

## What Could Have Invalidated It

- Compensating control 1: Supported: the patch hardens deadline enforcement in off-chain challenger state synchronization.
- Compensating control 2: Supported: before the fix, expired but `Unchallenged` games could be misclassified as locally challengeable.

## Severity Guidance

- Expected impact band: `integrity_or_policy_enforcement`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported: the patch hardens deadline enforcement in off-chain challenger state synchronization.
- Caution 2: Supported: before the fix, expired but `Unchallenged` games could be misclassified as locally challengeable.
