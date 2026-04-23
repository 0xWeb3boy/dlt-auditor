# Code-Shape Card

## Metadata

- ID: `go-ethereum-2024-05-07-go-ethereum-transaction-processing-e4b8058d5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-query-parameter`

## Code Shape Summary

- The FeeHistory path lacked an early cardinality limit for the rewardPercentiles input, leaving one caller-supplied query dimension unchecked while other dimensions such as block history length were already bounded.

## Search Motifs

- Motif 1: rpc method missing exact checks for unbounded query parameter
- Motif 2: security-sensitive path reaches expensive RPC-side computation, allocation, or response construction before rejecting malformed or unauthorized input
- Motif 3: Add an explicit upper bound for a caller-controlled query parameter and reject over-limit requests before expensive downstream processing

## Typical Asymmetry

- A cheap caller-controlled request dimension can scale expensive local computation, allocation, or persistent side effects.

## Patch Pattern

- Add an explicit upper bound for a caller-controlled query parameter and reject over-limit requests before expensive downstream processing.

## False Match Warnings

- Classify as security-hardening, not a proven security-fix.
- Limit claims to FeeHistory rewardPercentiles cardinality control.
