# Validation Card

## Metadata

- ID: `solana-2019-02-28-solana-staking-20e4edec61`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `vote-account-binding-confusion`

## What Confirmed The Issue

- Removed comment explicitly described a vote-account hijack and leader-rotation insertion risk.
- Vote account initialization now rejects a missing signer before deriving staker identity from account[0].

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
