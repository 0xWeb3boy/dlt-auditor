# Validation Card

## Metadata

- ID: `base-2026-03-26-base-storage-78f00388d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `nonce-validation`

## What Confirmed The Issue

- Evidence 1: The commit message explicitly says nonce validation was missing and is now enforced against state.
- Evidence 2: The handler previously performed a blind nonce-slot write based on transaction input without a preceding state read.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: this commit adds missing stateful nonce validation immediately before updating a nonce slot.
- Compensating control 2: Supported claim: the change removes a risky blind state update in replay-sensitive logic.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: this commit adds missing stateful nonce validation immediately before updating a nonce slot.
- Caution 2: Supported claim: the change removes a risky blind state update in replay-sensitive logic.
