# Validation Card

## Metadata

- ID: `solana-2023-06-20-solana-consensus-20a7cdd43d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-exposure`

## What Confirmed The Issue

- Commit subject and body explicitly describe restricting access to Bank HardForks.
- Commit body says prior callers could obtain read/write locks and modify HardForks from any Bank.

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
