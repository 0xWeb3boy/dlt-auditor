# Validation Card

## Metadata

- ID: `solana-2018-03-02-solana-cryptography-36bb1f989d`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `double-spend-stale-accounting`

## What Confirmed The Issue

- Commit subject names a double-spend attack directly.
- Commit body describes a spend-before-processing window and immediate balance updates as the fix.

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
