# Validation Card

## Metadata

- ID: `sei-chain-2024-05-08-sei-chain-transaction-processing-a2ab1c532`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `monetary-accounting-invariant`

## What Confirmed The Issue

- Evidence 1: Ante surplus is moved from derived transaction metadata to keeper-managed state keyed by transaction hash.
- Evidence 2: EndBlock now aggregates ante surplus with deferred EVM surplus and only adds balances when the net surplus is positive.

## What Could Have Invalidated It

- Compensating control 1: The accounting path affects only diagnostics and not balances or supply.
- Compensating control 2: A later invariant check aborts the block before committing mismatched state.

## Severity Guidance

- Expected impact band: economic-or-ledger-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The accounting path affects only diagnostics and not balances or supply.
- Caution 2: A later invariant check aborts the block before committing mismatched state.
