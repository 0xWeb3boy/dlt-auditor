# Code-Shape Card

## Metadata

- ID: `movement-2024-10-02-movement-transaction-processing-3bf63c914`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `transaction-sequence-number-reuse`

## Code Shape Summary

- Sequence-number admission relied on committed checkpoint state and did not visibly account for locally pending or reserved sequence numbers. The fix centralizes validation through a helper that checks a used-sequence-number pool before falling back to committed state, with TTL-based garbage collection for local reservations.

## Search Motifs

- transaction.sequence_number checked only against latest committed account state
- mempool admission accepts duplicate sender sequence before commit
- used/pending nonce pool added beside core mempool garbage collection
- helper returns invalid status before transaction forwarding

## Typical Asymmetry

- Committed state is authoritative for durable account sequence, but local pending state may be ahead and must still constrain admission.

## Patch Pattern

- Add a local used-sequence reservation pool, route admission through one helper that checks local and committed state, reject invalid sequence numbers before forwarding, and garbage-collect reservations on the mempool GC cadence.

## False Match Warnings

- Do not flag if another path atomically reserves sender sequence numbers before this check.
- Do not claim confirmed exploitability without insertion behavior, tests, or an advisory.
- A rejected duplicate for the same signer may be ordinary nonce handling unless the old path could forward or execute it.
