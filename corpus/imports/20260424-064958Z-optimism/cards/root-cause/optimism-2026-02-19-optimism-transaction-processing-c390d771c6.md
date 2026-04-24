# Root-Cause Card

## Metadata

- ID: `optimism-2026-02-19-optimism-transaction-processing-c390d771c6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-and-failure-isolation`

## Violated Invariant

- Invariant: Channel decompression must enforce MAX_RLP_BYTES_PER_CHANNEL during decoding so compressed input cannot cause unbounded output growth; if the stream exceeds the limit or later errors, only the bounded prefix is treated as channel content.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: availability

## Short Reusable Lesson

- Channel decompression must enforce MAX_RLP_BYTES_PER_CHANNEL during decoding so compressed input cannot cause unbounded output growth; if the stream exceeds the limit or later errors, only the bounded prefix is treated as channel content. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce resource-and-failure-isolation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
