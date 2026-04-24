# Validation Card

## Metadata

- ID: `sei-chain-2026-01-29-sei-chain-transaction-processing-bded875b1`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `mock-balance-mainnet-guard`

## What Confirmed The Issue

- Evidence 1: Mock balance mutation/top-off paths add explicit `s.ctx.ChainID() == "pacific-1"` panic checks with comments describing mainnet safety and critical misconfiguration.
- Evidence 2: The affected code is under `mock_balances` build-tag files and can add funds via bank keeper balance operations.

## What Could Have Invalidated It

- Compensating control 1: The build tag cannot be enabled in production artifacts.
- Compensating control 2: Every mutation path has a direct chain-ID or network guard.

## Severity Guidance

- Expected impact band: economic-or-ledger-integrity
- Expected severity band: low_or_informational

## False-Positive Cautions

- Caution 1: The build tag cannot be enabled in production artifacts.
- Caution 2: Every mutation path has a direct chain-ID or network guard.
