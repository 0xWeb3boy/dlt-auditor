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

Search patterns:
- pending callbacks that accept any reply of a given type or from a given peer
- validation that checks object identity but not parent, predecessor, chain segment, or request token
- loops that continue after only already-known items, empty batches, or zero net progress
- peer metadata used to enqueue work before validating supported type, bounds, compatibility, or lineage
- shared sender, authority, account, or reservation handles enforced in one pool but not another
- invalid, empty, timeout, and retry paths that do not update peer penalties symmetrically
- resource caps enforced on insertion while cleanup, reinsertion, continuation, or alternate ingress paths use weaker predicates

Questions to answer:
1. What exact request is this response supposed to satisfy?
2. What token, nonce, parent, predecessor, or lineage proves that binding?
3. Can the peer cause more work without making forward progress?
4. Are queue, reservation, or fetch limits enforced before expensive work is scheduled?
5. Do invalid and no-progress outcomes feed back into peer scoring, eviction, or throttling?
6. Are multiple subpools, queues, or ingress paths sharing one underlying resource without one shared reservation policy?

Severity guidance:
- Medium by default for sync-integrity or resource-exhaustion issues.
- High if the bug can make the node trust an attacker-controlled chain segment or broadly destabilize synchronization across peers.
```
