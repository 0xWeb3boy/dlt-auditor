# Prompt Family: Peer Sync, Progress, And Response Binding

## Use This For

- Downloader, header, body, state, or snapshot sync pipelines.
- Discovery ping or pong and bonding flows.
- Transaction announcement and fetch scheduling.
- Peer-driven queues, reservations, and bad-peer feedback loops.
- Any long-lived peer state machine where remote metadata can trigger more work.

## Prompt

```text
Hunt for vulnerabilities in peer-driven synchronization, discovery, and fetch pipelines in a blockchain or DLT codebase.

Focus on long-lived request/response state machines where untrusted peers can:
- satisfy a pending check with only a partial match,
- make the node keep working without forward progress,
- trigger expensive fetches from invalid metadata,
- reuse queue or reservation capacity across pools,
- avoid peer-quality penalties on invalid, empty, or zero-progress responses.

Prioritize:
- downloader, header sync, body sync, state sync, snapshot sync
- tx announcements and tx fetch scheduling
- discovery ping or pong and bonding
- peer scoring, bad-peer marking, retry, and eviction logic
- validator, authority, committee, sequencer, or relayer fanout where a client/node gathers certificates, effects, votes, checkpoint data, or execution results from multiple remote authorities

Search patterns:
- pending callbacks that accept any reply of a given type or from a given peer
- validation that checks object identity but not parent, predecessor, chain segment, or request token
- loops that continue after only already-known items, empty batches, or zero net progress
- peer metadata used to enqueue work before validating supported type, bounds, compatibility, or lineage
- shared sender, authority, account, or reservation handles enforced in one pool but not another
- invalid, empty, timeout, and retry paths that do not update peer penalties symmetrically
- resource caps enforced on insertion while cleanup, reinsertion, continuation, or alternate ingress paths use weaker predicates
- sync termination or "peer has stronger chain" decisions that accept a peer's claim without proving header progress, expected parentage, or a concrete chain segment beyond the local head
- discovery, bonding, ping/pong, or handshake responses where a reply of the right type is accepted without matching the exact challenge, nonce, peer identity, previous bond, or request token that authorized the larger response or state transition
- spoofable or unauthenticated discovery requests that can trigger larger responses, table lookups, peer-table mutation, or recursive lookup work before bonding, reachability, nonce, or token validation
- queue insertion, response-processing, or hash/body/state delivery APIs that return only success/failure when callers need to know whether the peer contributed new work, made zero progress, returned duplicate data, or revealed an unknown parent
- transaction, block, or state announcements where metadata validation, known-object checks, type support, and size bounds happen after the fetch request is already scheduled
- aggregation code that treats one authority response as enough to decide retry, liveness, or error classification before checking whether another authorized peer can provide the missing certificate, effects, proof, or vote
- response handlers that collapse Byzantine, malformed, empty, already-known, unavailable, timeout, and wrong-ledger responses into one generic error, preventing retry, bad-peer feedback, or invalid-data handling from taking the correct branch
- peer-abuse counters whose ownership is split from peer lifecycle ownership. If the reactor owns peer identity, disconnect, and cleanup events, counters that drive eviction should live there or be explicitly cleaned up there
- blacklist or eviction triggers attached to broad validation failures. Distinguish malformed, oversized, invalid-protocol, no-progress, and ordinary application-invalid inputs before penalizing a peer
- p2p mux or stream discriminators where a missing kind, mismatched kind, or default kind can create or reuse a stream under the wrong resource bucket

Questions to answer:
1. What exact request is this response supposed to satisfy?
2. What token, nonce, parent, predecessor, or lineage proves that binding?
3. Can the peer cause more work without making forward progress?
4. Are queue, reservation, or fetch limits enforced before expensive work is scheduled?
5. Do invalid and no-progress outcomes feed back into peer scoring, eviction, or throttling?
6. Are multiple subpools, queues, or ingress paths sharing one underlying resource without one shared reservation policy?
7. Does the response handler distinguish made-progress, duplicate/no-progress, stale, unknown-parent, invalid, and benign-empty outcomes?
8. Can a small request or announcement force a larger response, lookup, or fetch before the peer has proven reachability or supplied valid metadata?

Severity guidance:
- Medium by default for sync-integrity or resource-exhaustion issues.
- High if the bug can make the node trust an attacker-controlled chain segment or broadly destabilize synchronization across peers.
```
