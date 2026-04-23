# Root-Cause Card

## Metadata

- ID: `nitro-2026-02-12-nitro-transaction-processing-66d78e539`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-divergence`
- Confidence tier: `tier_a_confirmed`

## Missing Property

- Missing property: `atomic-derived-transaction-processing`

## Violated Invariant

- Invariant: A user transaction and its derived retryable auto-redeems should be processed atomically for consensus so that a filter failure in a derived redeem reverts the entire group.

## Trust Boundary

- Boundary: `transaction execution->derived retryable redeem processing`

## Attack Surface

- Entrypoint type: `block-production-or-transaction-group-processing`
- Sensitive sink: `finalizing block state for a user transaction and its derived redeems`

## Impact Pattern

- Primary impact: `state-integrity`
- Secondary impact: `none`

## Short Reusable Lesson

- A user transaction and its derived retryable auto-redeems should be processed atomically for consensus so that a filter failure in a derived redeem reverts the entire group. The evidence supports a consensus-divergence fix in `ProduceBlockAdvanced` for retryable auto-redeems. The patch adds group-level checkpointing around a user transaction and its generated redeems so that if a redeem triggers `state.ErrArbTxFilter`, the whole tentative group is reverted rather than only dropping the redeem. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
