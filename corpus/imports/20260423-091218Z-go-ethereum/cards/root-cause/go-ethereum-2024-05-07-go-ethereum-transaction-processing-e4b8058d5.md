# Root-Cause Card

## Metadata

- ID: `go-ethereum-2024-05-07-go-ethereum-transaction-processing-e4b8058d5`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `unbounded-query-parameter`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `input-validation`

## Violated Invariant

- Invariant: TODO

## Trust Boundary

- Boundary: TODO

## Attack Surface

- Entrypoint type: TODO
- Sensitive sink: TODO

## Impact Pattern

- Primary impact: TODO
- Secondary impact: TODO

## Short Reusable Lesson

- The patch adds a maximum cardinality check for the rewardPercentiles argument in Oracle.FeeHistory. Requests with more than 100 percentiles now fail early with an errInvalidPercentile-derived error. This is supported as DDoS/resource-control hardening, mainly by the explicit commit message and the added query bound, but the evidence does not prove a concrete exploit, crash, or quantified amplification.
