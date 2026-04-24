# Prompt Family: Resource Accounting And Limits

## Use This For

- Missing gas charging.
- Simulation paths that skip metering.
- Weight or queue limits enforced on the wrong representation.
- Mempool, scheduler, or batching resource-limit mismatches.
- Consensus safety floors not enforced during election or admission.

## Prompt

```text
Hunt for resource-accounting bugs in a blockchain or DLT codebase.

Focus on code that performs expensive work before charging gas or fees, before applying quotas or weight limits, or before queue admission can fail cleanly.

Prioritize:
- mempool, txpool, scheduler, or block-builder code
- admission and execution handlers
- simulation or estimation flows
- bridge or batch processing handlers
- quota, rate-limit, and spam-protection code
- RPC, WebSocket, admin, query, publish, and session-setup ingress

Search patterns:
- handlers that start with state reads, runtime lookups, proof parsing, or validation before UseGas or an equivalent charge
- simulation checks placed before charging
- admission checks done on raw transaction size instead of checked transaction weight, byte cost, proof cost, or resource units
- queue insertion that can fail after validation but without mapping failure back to the originating tx
- minimum or threshold parameters validated in one place but not enforced where the decision is made
- relay, oracle, or scheduler paths that forward measured or observed values without final caps, floors, or sanity bounds at the submission sink
- timeouts without semaphore caps, concurrency limits, or load shedding
- accept loops or handlers that spawn per-connection or per-request work before acquiring admission permits
- backlog growth controls that protect one ingress path but leave alternate RPC or publisher paths effectively unbounded
- streaming sync, fetch, or announcement loops that continue after only already-known items, empty batches, or zero net progress
- compressed protocol input should enforce output limits at the decompression boundary, including partial-output and repeated-read behavior. Do not rely only on later parsers to discover that decompressed bytes exceeded the channel, batch, or message cap
- per-item parsing failures in derived input streams should be isolated when the protocol allows skipping or reporting bad items; one malformed child object should not abort a whole parent batch unless that is the consensus rule
- multi-dimensional limits where one path enforces count but not bytes, bytes but not count, or uses `both limits exceeded` where the policy says `any limit exceeded`
- cleanup or truncation paths that use a weaker predicate than insertion/admission paths
- cache-hit paths that return stored execution or precompile result objects containing gas, quota, reservoir, refund, or caller-local accounting state
- batch-mode decisions that choose clean, incremental, bounded, or unbounded work based only on the next local window instead of the full remaining range
- shared sender, authority, account, or reservation handles enforced in one pool, queue, or subpool but not in the others that consume the same underlying resource
- cross-language, cross-process, or offloaded execution APIs that receive a mutable budget, gas, or quota on entry but do not return the remaining budget to the authoritative charging layer
- recovery or trap-handling paths that retry with larger stacks, buffers, or allocations without a one-time guard, context restriction, or outer quota
- parent operations that spawn derived work where the parent is charged, finalized, or committed before the child work proves cleanly met the same accounting or filter rules
- historical-range, log, trace, fee-history, proof, or witness APIs where the configured range limit is checked in one entrypoint but not in stored-filter replay, chain-specific variants, symbolic latest/pending/finalized selectors, or helper paths that construct the same expensive query
- background verification, sync-maintenance, pruning, and repair loops that derive their work window from current head minus a checkpoint, milestone, or finalized boundary. Check that the trusted boundary is fresh, the window is capped before materializing work, and missing boundary data disables or defers the loop instead of scanning an unbounded range
- transaction types that auto-create trust lines, holdings, directories, tickets, delegate objects, shares, receipts, or other state entries as a side effect. Check that reserve, owner-count, spam-cost, and quota accounting is enforced before the auto-created object reaches durable state
- failed protocol handshakes, upgrades, peer sessions, or admission attempts where resource or session accounting is allocated before verification. Rejection paths must release or charge the same resource state as successful handoff paths

Questions to answer:
1. What resource is the protocol trying to meter: gas, fees, bytes, weight, queue slots, proving budget, bridge capacity, committee size, or sender concurrency?
2. When is it charged or enforced?
3. Is there a path that performs meaningful work before that point?
4. Does simulation use the same accounting path as live execution?
5. Are errors propagated back to the correct transaction and caller?
6. Are front-door services bounded before expensive handshake, parsing, or per-client task creation?
7. Can a peer or caller keep the system busy without making forward progress or consuming the same reservation accounting as successful work?
8. If work crosses a subsystem boundary, which layer is authoritative for charging the consumed budget, and does that layer learn the post-execution remaining budget instead of assuming the callee charged it correctly?
9. If the code retries after a fault, what prevents repeated resource growth or repeated expensive recovery for the same failing invocation?
10. Can one user action create derived state entries or sessions that consume reserve, ownership slots, queue capacity, or cleanup work not charged to the actor?
11. Do failed handshake or admission paths release exactly the same reservations, sessions, and per-peer counters that success paths transfer to the next owner?

Severity guidance:
- Medium by default for DoS, fee bypass, and resource exhaustion.
- Raise only if the missing limit can destabilize consensus, settlement, bridge processing, or systematically underprice privileged operations.
```
