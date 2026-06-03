# Proposal Cardinality And Retained State Growth

## Family Objective

Find liveness and resource bugs where proposal validation accepts missing required system work, many syntactically valid empty or low-work objects, or valid-but-useless retained objects that later force expensive scans, verification, storage growth, or repeated cleanup.

## Hunt Steps

1. Enumerate proposal, block, batch, aggregate, vote, receipt, pending-job, claim, attestation, and message containers.
2. For each container, record lower bounds, upper bounds, byte-size limits, count limits, gas or weight limits, per-sender/per-validator limits, and required object types.
3. Test missing required system work separately from many empty or no-op objects. A validator may reject unknown object types but still accept zero mandatory objects or many valid empty objects.
4. For each accepted object, trace decode cost, signature/proof cost, database writes, emitted receipts, retained rows, indexes, and every future iteration or pruning path.
5. Build a capacity equation:
  - attacker-controlled objects per proposal or block,
  - blocks per retention window,
  - cleanup or prune lag,
  - repeated scans per block or per approval attempt,
  - expensive operations per object.
6. Search for valid-but-useless retained objects: fake roots, empty receipts, invalid-later claims, duplicate-semantic votes with unique roots, zero-effect transactions, no-op messages, failed delivery records, proof jobs, and retryable tasks.
7. Check whether rejection happens before or after persistence. Objects inserted before later duplicate, membership, signature, or sink checks can still cause storage growth even if useful data is rejected.
8. Compare proposer construction with validator acceptance. If honest builders never create empty/missing/many objects, still verify whether validators accept them from a byzantine proposer.
9. Check disk and restart impact: retained objects that are harmless in memory can become liveness issues when persisted, replayed, exported, compacted, or scanned after restart.
10. Identify the smallest proof: one proposal with many empty objects, one block with maximum no-op objects, or a symbolic retention equation showing unbounded or large growth under protocol limits.
11. For empty or no-op transactions, inspect validator-side proposal acceptance directly. Honest builders may filter them, but the issue exists if byzantine proposers can include syntactically valid empty entries that validators decode, store, hash, replay, or otherwise process without proportional charging.
12. For retained fake roots or pending attestations, trace the object through insertion, persistence key, approval or consumption, pruning/trim, query/export, restart/replay, and per-block iteration. Keep roots that are useless for protocol progress but valid enough to persist.
13. Separate "number of useful objects" from "number of distinct keys". If an attacker can vary root, signature bytes, metadata, source height, or envelope bytes while targeting the same semantic period, compute growth using the distinct persistence key.
14. When cleanup exists, compare cleanup frequency with insertion frequency. Cleanup that runs only after approval, every N blocks, on epoch changes, or behind a finalized/trim lag may still permit large retained sets.

## Candidate Requirements

For every candidate, include:

- container and entrypoint;
- missing lower bound or weak upper bound;
- accepted empty/no-op/useless object shape;
- persistence and future iteration path;
- capacity equation with known or symbolic bounds;
- attacker role and cost;
- concrete liveness, disk, CPU, replay, or cleanup impact;
- focused proof or benchmark that would confirm the estimate.
- whether the path was accepted by validators or only produced by honest builders.

## False-Positive Controls

- Do not report mere inefficiency without attacker-controlled admission and a repeated or persistent cost.
- Do not report state growth if cleanup runs before any expensive repeated consumer can observe it.
- Do not report many-object DoS if byte/gas/count limits tightly bound total work and the work is charged proportionally.
- Distinguish censorship or omitted optional work from accepted malformed protocol state; missing mandatory system work is stronger than ordinary proposer choice.
