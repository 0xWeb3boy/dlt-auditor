# Validation Card

## Metadata

- ID: `go-ethereum-2024-05-07-go-ethereum-transaction-processing-e4b8058d5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-query-parameter`

## What Confirmed The Issue

- Evidence 1: Commit subject/body explicitly says the query limit was added to defend against DDoS.
- Evidence 2: FeeHistory now rejects len(rewardPercentiles) greater than maxQueryLimit before further processing.

## What Could Have Invalidated It

- Compensating control 1: Classify as security-hardening, not a proven security-fix.
- Compensating control 2: Limit claims to FeeHistory rewardPercentiles cardinality control.

## Severity Guidance

- Expected impact band: medium
- Expected severity band: medium

## False-Positive Cautions

- Caution 1: Classify as security-hardening, not a proven security-fix.
- Caution 2: Limit claims to FeeHistory rewardPercentiles cardinality control.
