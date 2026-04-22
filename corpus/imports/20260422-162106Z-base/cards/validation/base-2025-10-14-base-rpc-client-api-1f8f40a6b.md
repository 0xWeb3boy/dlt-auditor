# Validation Card

## Metadata

- ID: `base-2025-10-14-base-rpc-client-api-1f8f40a6b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-state-validation`

## What Confirmed The Issue

- Evidence 1: Commit message explicitly says cached checkpoints are now validated against the contract before reuse.
- Evidence 2: The proposer logic changed from direct reuse of checkpointed L1 hash/number to conditional reuse only when it still matches the on-chain mapping.

## What Could Have Invalidated It

- Compensating control 1: Supported claim: the commit hardens a sensitive flow by revalidating cached checkpoint state against on-chain canonical data before reuse.
- Compensating control 2: Not supported: that this was a proven exploitable vulnerability or a confirmed consensus-break bug.

## Severity Guidance

- Expected impact band: `state_or_consensus_integrity`
- Expected severity band: `medium_or_low`

## False-Positive Cautions

- Caution 1: Supported claim: the commit hardens a sensitive flow by revalidating cached checkpoint state against on-chain canonical data before reuse.
- Caution 2: Not supported: that this was a proven exploitable vulnerability or a confirmed consensus-break bug.
