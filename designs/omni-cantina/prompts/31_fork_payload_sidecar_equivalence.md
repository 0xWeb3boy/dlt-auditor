# Fork Payload Sidecar Equivalence

## Family Objective

Find bugs where transactions, blocks, or execution payloads carry fork-specific detached data, but validators, importers, or retry loops pass side arguments that do not match the committed payload.

## Hunt Steps

1. Enumerate every transaction or block object that can carry detached data, commitments, hashes, sidecars, optional fork fields, data-availability references, withdrawals, or fork-specific roots.
2. Trace the object across user admission, mempool/storage, honest builder construction, block-body encoding, proposal serialization, validator decoding, local verification, execution-client import, replay, and recovery.
3. Build a table with one row per detached field:
   - payload field or commitment;
   - sidecar or side argument;
   - producer of each value;
   - where equality or presence is checked;
   - what happens when the side argument is empty, nil, default, stale, or independently computed.
4. Compare method or fork version with field presence. A fork-versioned import method should receive the exact side data required by that method and payload version.
5. Search for code that discards sidecars while preserving payloads, rebuilds only part of the payload envelope, or supplies empty arrays/maps for side arguments.
6. Classify execution/import errors. Deterministic malformed-payload, unsupported-method, invalid-sidecar, and fork-field errors should not be retried as transient transport errors inside consensus callbacks.
7. Compare proposer behavior with validator behavior. If the proposer creates a valid payload with side data but validators reconstruct or import it without the same data, the validator path is the critical sink.
8. Design a minimal proof: one payload requiring detached data, one validator reconstruction path, and one mock or source-backed dependency result showing reject, retry, or halt behavior.

## Candidate Requirements

For every candidate, include:

- object type and fork/version gate;
- committed payload field requiring detached data;
- missing, empty, stale, or independently supplied side argument;
- exact proposer path and validator/import path;
- equality or presence check that should have run;
- dependency error class and retry/rejection behavior;
- concrete consensus, liveness, or state-execution impact;
- minimal test or mock that would confirm the mismatch.

## False-Positive Controls

- Do not report detached data that is not committed, not enabled by the current fork or feature gate, or not accepted from untrusted proposers.
- Do not report an execution-client rejection if the application deterministically rejects the proposal and does not retry or commit partial work.
- Do not assume a side argument is wrong because it is empty; prove the payload can require it.
