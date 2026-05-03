# Validation Card

## Metadata

- ID: `firedancer-2026-04-14-firedancer-staking-22a2fea5d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `missing-owner-check`

## What Confirmed The Issue

- Evidence 1: A new helper rejects accounts whose meta->owner does not match the Solana vote program id.
- Evidence 2: The helper then delegates to the existing size-and-initialization vote-state validation.

## What Could Have Invalidated It

- Compensating control 1: No evidence shows that an attacker can create or route a non-vote-owned account into these paths.
- Compensating control 2: No regression test or exploit scenario is supplied demonstrating the bad pre-patch behavior.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: No evidence shows that an attacker can create or route a non-vote-owned account into these paths.
- Caution 2: No regression test or exploit scenario is supplied demonstrating the bad pre-patch behavior.
