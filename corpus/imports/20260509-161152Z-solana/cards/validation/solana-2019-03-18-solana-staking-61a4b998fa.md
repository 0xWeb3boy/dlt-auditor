# Validation Card

## Metadata

- ID: `solana-2019-03-18-solana-staking-61a4b998fa`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-safety-hardening`

## What Confirmed The Issue

- Replay-stage voting changed from TODO/latest-slot selection to locktower voting logic.
- BankForks gained ancestry mapping used for fork-aware vote decisions.

## What Could Have Invalidated It

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.

## Severity Guidance

- Expected impact band: integrity_or_funds
- Expected severity band: High
- Rationale: The impact can affect funds, consensus safety, authorization boundaries, or runtime integrity when reachable.

## False-Positive Cautions

- A prior canonical validator rejects the input before it reaches the sensitive sink.
- The affected path is test-only, admin-only, or unreachable in production builds.
- The apparent missing check is enforced by a shared callee on every equivalent path.
