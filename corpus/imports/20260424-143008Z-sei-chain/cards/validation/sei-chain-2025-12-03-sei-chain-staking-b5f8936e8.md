# Validation Card

## Metadata

- ID: `sei-chain-2025-12-03-sei-chain-staking-b5f8936e8`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-nondeterminism-hardening`

## What Confirmed The Issue

- Evidence 1: Commit body states different precompile error messages can lead to app hash differences.
- Evidence 2: Commit body states resultsHash is derived from marshalled transaction results and only deterministic fields should be included.

## What Could Have Invalidated It

- Compensating control 1: Failure data is omitted from committed results.
- Compensating control 2: The VM error channel signals failure while return data is nil or fixed.

## Severity Guidance

- Expected impact band: consensus-integrity-or-liveness
- Expected severity band: high_or_medium

## False-Positive Cautions

- Caution 1: Failure data is omitted from committed results.
- Caution 2: The VM error channel signals failure while return data is nil or fixed.
