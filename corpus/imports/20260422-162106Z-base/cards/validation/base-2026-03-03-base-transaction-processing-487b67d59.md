# Validation Card

## Metadata

- ID: `base-2026-03-03-base-transaction-processing-487b67d59`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `input-validation`

## What Confirmed The Issue

- Evidence 1: `load_blobs` now returns `ResetError::BlobsOverFill` when fetched blobs remain unused after fill, enforcing an exact-match invariant.
- Evidence 2: A new `ResetError::BlobsOverFill(usize, usize)` variant was added specifically to represent the mismatch condition.

## What Could Have Invalidated It

- Compensating control 1: The diff supports an integrity hardening interpretation in a consensus-sensitive path, not proof of a concrete exploitable vulnerability.
- Compensating control 2: The patch should not be described as fixing memory safety, authentication, or authorization issues.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: The diff supports an integrity hardening interpretation in a consensus-sensitive path, not proof of a concrete exploitable vulnerability.
- Caution 2: The patch should not be described as fixing memory safety, authentication, or authorization issues.
