# Root-Cause Card

## Metadata

- ID: `movement-2024-10-02-movement-transaction-processing-3bf63c914`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-number-reuse`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `local-sequence-reservation-check`

## Violated Invariant

- Invariant: A transaction admission path must reject an account sequence number that is already pending, reserved, or recently used locally; committed checkpoint state alone is not enough while local mempool state is ahead of durable state.

## Trust Boundary

- Boundary: Externally submitted signed transactions crossing from mempool/RPC ingestion into the execution transaction pipe.

## Attack Surface

- Entrypoint type: transaction submission / mempool admission
- Sensitive sink: core mempool insertion and forwarding into the execution pipeline

## Impact Pattern

- Primary impact: Replay or duplicate transaction admission before durable state advances.
- Secondary impact: State-ordering confusion or wasted mempool/execution work.

## Short Reusable Lesson

- Sequence-number admission relied on committed checkpoint state and did not visibly account for locally pending or reserved sequence numbers. The fix centralizes validation through a helper that checks a used-sequence-number pool before falling back to committed state, with TTL-based garbage collection for local reservations. Add a local used-sequence reservation pool, route admission through one helper that checks local and committed state, reject invalid sequence numbers before forwarding, and garbage-collect reservations on the mempool GC cadence.
