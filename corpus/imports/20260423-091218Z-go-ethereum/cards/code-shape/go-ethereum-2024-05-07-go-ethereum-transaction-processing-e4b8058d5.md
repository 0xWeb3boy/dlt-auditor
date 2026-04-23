# Code-Shape Card

## Metadata

- ID: `go-ethereum-2024-05-07-go-ethereum-transaction-processing-e4b8058d5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-query-parameter`

## Code Shape Summary

- The patch adds a maximum cardinality check for the rewardPercentiles argument in Oracle.FeeHistory. Requests with more than 100 percentiles now fail early with an errInvalidPercentile-derived error. This is supported as DDoS/resource-control hardening, mainly by the explicit commit message and the added query bound, but the evidence does not prove a concrete exploit, crash, or quantified amplification.

## Search Motifs

- Motif 1: TODO
- Motif 2: TODO
- Motif 3: TODO

## Typical Asymmetry

- TODO

## Patch Pattern

- TODO

## False Match Warnings

- TODO
