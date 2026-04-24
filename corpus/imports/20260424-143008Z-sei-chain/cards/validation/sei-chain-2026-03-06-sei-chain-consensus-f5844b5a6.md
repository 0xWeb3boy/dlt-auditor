# Validation Card

## Metadata

- ID: `sei-chain-2026-03-06-sei-chain-consensus-f5844b5a6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`

## What Confirmed The Issue

- Evidence 1: Production consensus code changed TimeoutVote construction from always using current i.PrepareQC to using current-or-inherited PrepareQC.
- Evidence 2: Inline comment states consecutive timeouts could lose the lock and allow a conflicting proposal to be committed.

## What Could Have Invalidated It

- Compensating control 1: The protocol forbids entering the new view without separately restoring the lock.
- Compensating control 2: Proposal verification independently rejects conflicts without relying on TimeoutVote PrepareQC.

## Severity Guidance

- Expected impact band: consensus-integrity-or-liveness
- Expected severity band: high_or_medium

## False-Positive Cautions

- Caution 1: The protocol forbids entering the new view without separately restoring the lock.
- Caution 2: Proposal verification independently rejects conflicts without relying on TimeoutVote PrepareQC.
