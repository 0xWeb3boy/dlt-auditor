# Validation Card

## Metadata

- ID: `sei-chain-2025-05-06-sei-chain-rpc-client-api-4523d3d13`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `check-then-set-race`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly says "Harden oracle tx spam prevention".
- Evidence 2: The ante decorator replaces separate GetSpamPreventionCounter and SetSpamPreventionCounter calls with CheckAndSetSpamPreventionCounter.

## What Could Have Invalidated It

- Compensating control 1: Ante handling for the actor is strictly serialized by the mempool/executor.
- Compensating control 2: A database transaction enforces uniqueness for the counter key.

## Severity Guidance

- Expected impact band: protocol-state-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: Ante handling for the actor is strictly serialized by the mempool/executor.
- Caution 2: A database transaction enforces uniqueness for the counter key.
