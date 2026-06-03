# Retained Aggregate Root Growth

## Family Objective

Find liveness bugs where validators, proposers, peers, or users can create many valid-but-useless aggregate roots, votes, receipts, claims, or pending objects that persist until approval, trim, pruning, or restart and are repeatedly scanned or verified.

## Hunt Steps

1. Enumerate pending-object stores and tables: aggregate roots, votes, signatures, receipts, claims, proof jobs, retryables, bridge messages, attestations, approvals, and cleanup indexes.
2. For each store, identify insertion paths, persistence key fields, per-block or per-sender limits, required authorization, duplicate checks, and semantic usefulness checks.
3. Search for distinct persistence keys that represent the same semantic period, signer set, source height, claim window, or approval target. Root-only or byte-only uniqueness is suspicious when useless variants can multiply.
4. Trace consumption and cleanup: approval, quorum, finalization, trim lag, pruning, garbage collection, export, query, restart replay, and every-block iteration.
5. Build a capacity equation:
   - attacker-controlled inserts per block;
   - number of blocks retained;
   - maximum distinct keys per semantic target;
   - repeated scans or expensive operations per block/approval;
   - storage and replay cost.
6. Distinguish rejected useful progress from accepted useless state. A store can be DoS-relevant when objects are valid enough to persist but invalid or irrelevant for approval.
7. Check whether cleanup depends on honest progress that the attacker can delay, such as quorum approval, finalized height, external chain finality, or trim lag.
8. Design the smallest proof: insert many cheap distinct roots or objects for one semantic window, then trigger the iterator, approval, trim, query, restart, or block-finalization path that scales with retained count.

## Candidate Requirements

For every candidate, include:

- pending store and persistence key;
- insertion path and attacker role;
- why each object is valid enough to persist but useless for progress;
- cleanup/retention condition and repeated consumer;
- capacity equation with symbolic or concrete bounds;
- impact on proposal validation, finalization, approval, query, disk, replay, or block time;
- minimal proof or benchmark.

## False-Positive Controls

- Do not report state growth without attacker-controlled insertion and a consumer that scales with retained objects.
- Do not report retained objects that are promptly cleaned before expensive consumers can observe them.
- Do not treat a small fixed protocol bound as unbounded; use the actual or symbolic limit in the capacity equation.
