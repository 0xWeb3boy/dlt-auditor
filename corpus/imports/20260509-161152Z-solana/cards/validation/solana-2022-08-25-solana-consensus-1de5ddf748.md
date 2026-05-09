# Validation Card

## Metadata

- ID: `solana-2022-08-25-solana-consensus-1de5ddf748`
- Bug family: `checked_arithmetic_and_parameter_bounds`
- Bug class: `arithmetic-overflow-hardening`

## What Confirmed The Issue

- Unchecked slot offset addition in compact vote-state conversion was replaced with checked_add.
- Uncompaction now returns InstructionError::ArithmeticOverflow when root plus offset arithmetic overflows.

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
