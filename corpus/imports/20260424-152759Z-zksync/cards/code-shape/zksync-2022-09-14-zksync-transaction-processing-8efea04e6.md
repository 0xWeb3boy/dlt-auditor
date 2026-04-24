# Code-Shape Card

## Metadata

- ID: `zksync-2022-09-14-zksync-transaction-processing-8efea04e6`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `withdrawal-finalization-ordering`

## Code Shape Summary

- The finalizer changes from a coarse max-processed-block guard to a per-block max-log-index guard, and parsed withdrawal events now carry log_index. The reusable shape is event idempotency keyed too coarsely for streams where multiple distinct events share a block or batch.

## Search Motifs

- MAX(block_number) replaced with MAX(log_index) scoped by block
- event parser begins storing log_index or event_index
- duplicate-processing guard changes from block-level to event-level identity

## Typical Asymmetry

- The dangerous value originates outside the trusted state model, while the vulnerable code treats it as already canonical, authenticated, or uniquely identified.

## Patch Pattern

- Persist the source event log index, query processed progress within the same block, and compare block plus log index before deciding an event is already finalized.

## False Match Warnings

- If the protocol guarantees at most one relevant event per block, block-level idempotency may be sufficient.
- Parser assert-to-error changes are robustness signals, not proof of exploitability.
- Do not claim theft or arbitrary withdrawal creation without accounting evidence.
