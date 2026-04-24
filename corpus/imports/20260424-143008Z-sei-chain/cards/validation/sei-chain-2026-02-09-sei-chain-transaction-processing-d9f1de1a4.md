# Validation Card

## Metadata

- ID: `sei-chain-2026-02-09-sei-chain-transaction-processing-d9f1de1a4`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `app-hash-state-accounting-inconsistency`

## What Confirmed The Issue

- Evidence 1: Commit subject explicitly references fixes for app hash.
- Evidence 2: Patch changes consensus-sensitive block processing in app/app.go.

## What Could Have Invalidated It

- Compensating control 1: The alternate path is disabled in production.
- Compensating control 2: Downstream reads use the same cached store and cannot observe stale data.

## Severity Guidance

- Expected impact band: economic-or-ledger-integrity
- Expected severity band: medium_or_low

## False-Positive Cautions

- Caution 1: The alternate path is disabled in production.
- Caution 2: Downstream reads use the same cached store and cannot observe stale data.
