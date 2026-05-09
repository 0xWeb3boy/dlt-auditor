# Validation Card

## Metadata

- ID: `solana-2019-03-18-solana-staking-89c42ecd3f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-vote-safety-hardening`

## What Confirmed The Issue

- Replay-stage voting previously selected the latest frozen bank under a TODO fork-selection path.
- The patch integrates locktower voting into replay-stage vote selection.

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
