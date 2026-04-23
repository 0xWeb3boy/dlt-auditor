# Root-Cause Card

## Metadata

- ID: `nitro-2023-02-24-nitro-transaction-processing-e853315fb`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-version-gating`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `protocol-version-gating`

## Violated Invariant

- Invariant: Transaction parsing should gate transaction types on the active protocol version derived from canonical state, not on implicit assumptions or stale context.

## Trust Boundary

- Boundary: `transaction bytes->parser and replay logic`

## Attack Surface

- Entrypoint type: `transaction-or-batch-validation`
- Sensitive sink: `accepting or replaying a transaction type not yet enabled`

## Impact Pattern

- Primary impact: `unexpected-transaction-acceptance`
- Secondary impact: `consensus-integrity`

## Short Reusable Lesson

- Transaction parsing should gate transaction types on the active protocol version derived from canonical state, not on implicit assumptions or stale context. The patch makes L2 transaction parsing version-aware across block production and reorg replay, and adds an explicit rejection of `ArbitrumExtendedTxType` when `arbOSVersion < 11`. That supports a protocol-correctness invariant, but the provided evidence does not establish a concrete vulnerability rather than feature rollout and compatibility work. The robust fix is to make the privileged sink consume authoritative state or policy context that has already been validated, and fail closed when that binding is missing.
