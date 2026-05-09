# Validation Card

## Metadata

- ID: `solana-2020-12-15-solana-consensus-db339cb925`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-ordering-race`

## What Confirmed The Issue

- Commit subject identifies a race between tick height publication and accounts hash calculation.
- `Bank::register_tick` now rejects work once freezing has started, not only after the bank is frozen.

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
