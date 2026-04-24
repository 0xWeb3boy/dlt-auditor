# Root-Cause Card

## Metadata

- ID: `zksync-2022-09-14-zksync-transaction-processing-8efea04e6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `withdrawal-finalization-ordering`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `event-identity-idempotency`

## Violated Invariant

- Invariant: Event finalization idempotency must use a unique event identity such as block number plus log index; processing one event must not mark every event in the block as complete.

## Trust Boundary

- Boundary: L1 withdrawal logs cross into L2 withdrawal finalization storage and accounting state.

## Attack Surface

- Entrypoint type: `blockchain_event_ingestion`
- Sensitive sink: withdrawal finalization records and fund-availability state

## Impact Pattern

- Primary impact: withdrawal finalization state integrity
- Secondary impact: fund availability for skipped same-block events

## Short Reusable Lesson

- The finalizer changes from a coarse max-processed-block guard to a per-block max-log-index guard, and parsed withdrawal events now carry log_index. The reusable shape is event idempotency keyed too coarsely for streams where multiple distinct events share a block or batch.
