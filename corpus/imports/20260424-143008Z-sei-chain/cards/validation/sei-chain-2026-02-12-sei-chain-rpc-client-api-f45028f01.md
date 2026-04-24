# Validation Card

## Metadata

- ID: `sei-chain-2026-02-12-sei-chain-rpc-client-api-f45028f01`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-mismatch`

## What Confirmed The Issue

- Evidence 1: Consensus code now ignores proposals that mismatch an existing commit certificate during RoundStepCommit.
- Evidence 2: Commit handling now checks ProposalBlockParts against the certified blockID.PartSetHeader instead of only the proposal block hash.

## What Could Have Invalidated It

- Compensating control 1: The consensus state machine already clears conflicting proposal data before commit.
- Compensating control 2: Block parts are cryptographically bound and cannot be mixed across headers.

## Severity Guidance

- Expected impact band: availability-or-resource-control
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The consensus state machine already clears conflicting proposal data before commit.
- Caution 2: Block parts are cryptographically bound and cannot be mixed across headers.
