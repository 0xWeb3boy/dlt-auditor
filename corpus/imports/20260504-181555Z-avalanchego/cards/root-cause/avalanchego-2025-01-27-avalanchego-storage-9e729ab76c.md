# Root-Cause Card

## Metadata

- ID: `avalanchego-2025-01-27-avalanchego-storage-9e729ab76c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `rpc-resource-control`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rpc-parameter-cardinality-bound`

## Violated Invariant

- Invariant: Caller-controlled RPC arrays must be bounded before repeated processing, allocation, or per-element computation.

## Trust Boundary

- Boundary: Remote RPC parameters cross into backend fee-history computation.

## Attack Surface

- Entrypoint type: RPC fee history query
- Sensitive sink: looping, allocation, or percentile computation over caller-controlled reward percentile inputs

## Impact Pattern

- Primary impact: availability, resource-exhaustion
- Secondary impact: medium_availability

## Root Cause

- The only supported root cause is that the supplied pre-patch FeeHistory snippet lacks a cardinality bound on the caller-controlled rewardPercentiles array. The evidence does not support claiming state corruption, consensus divergence, cryptographic failure, replay failure, authentication failure, or authorization bypass. ## Walkthrough 1. A caller supplies blocks and a rewardPercentiles array to Oracle.FeeHistory. 2.

## Short Reusable Lesson

- A maxQueryLimit check was added for caller-supplied reward percentiles before fee-history processing. The reusable shape is an RPC endpoint that bounds array cardinality independently of per-element validation.
