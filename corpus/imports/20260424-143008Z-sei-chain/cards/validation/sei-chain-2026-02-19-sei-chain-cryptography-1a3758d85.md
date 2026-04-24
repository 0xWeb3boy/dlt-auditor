# Validation Card

## Metadata

- ID: `sei-chain-2026-02-19-sei-chain-cryptography-1a3758d85`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-proposal-validation-hardening`

## What Confirmed The Issue

- Evidence 1: New Proposal construction now checks key.Public() against committee.Leader(viewSpec.View()) and errors on mismatch.
- Evidence 2: A Proposal.Verify(c) method was added to validate every present lane range with LaneRange.Verify(c).

## What Could Have Invalidated It

- Compensating control 1: The constructor is private and all callers already validate these invariants.
- Compensating control 2: The verifier rejects the malformed proposal before consensus state mutation.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The constructor is private and all callers already validate these invariants.
- Caution 2: The verifier rejects the malformed proposal before consensus state mutation.
