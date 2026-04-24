# Root-Cause Card

## Metadata

- ID: `optimism-2026-02-19-optimism-transaction-processing-543510ee9b`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `resource-and-failure-isolation`

## Violated Invariant

- Invariant: Untrusted compressed channel data must not be able to expand without a configured per-channel output bound. Decompression should enforce max_rlp_bytes_per_channel at the decompression boundary rather than relying on decoder defaults.

## Trust Boundary

- Boundary: sequencer/batch/transaction input -> derivation or execution engine

## Attack Surface

- Entrypoint type: transaction-handler or batch-derivation path
- Sensitive sink: block payload acceptance, execution attributes, or derived state transition

## Impact Pattern

- Primary impact: availability
- Secondary impact: availability-or-liveness

## Short Reusable Lesson

- Untrusted compressed channel data must not be able to expand without a configured per-channel output bound. Decompression should enforce max_rlp_bytes_per_channel at the decompression boundary rather than relying on decoder defaults. Similar bugs appear when transaction-handler or batch-derivation path code treats partially checked input as authoritative and lets it reach block payload acceptance, execution attributes, or derived state transition. The reusable fix is to enforce resource-and-failure-isolation at the boundary and fail closed before state, privilege, or consensus-visible output changes.
