# Prompt Family: State Machine And Lifecycle Consistency

## Use This For

- Stale timeout, session, or policy state.
- Cleanup performed on one transition path but not another.
- Confusion between similar protocol coordinates.
- Cache or merge logic that breaks authenticated state assumptions.
- Role-scoped accounting applied to the wrong actors.

## Prompt

```text
Hunt for lifecycle and state-machine bugs in a blockchain or DLT codebase.

Look for code where the same logical object can transition through multiple paths, but cleanup, scoping, or accounting happens in only some of them.

Focus on:
- consensus round or view lifecycle
- session, channel, stream, bridge, or proof-submission state
- epoch, handoff, checkpoint, or validator-set rotation state
- committee aggregation and liveness accounting
- storage cache, proof cache, merge, and eviction logic

Search patterns:
- timeout or session fields that are cleared in finalize paths but not abort, reset, empty-block, retry, or redeploy paths
- terminal success, verified, finalized, or already-committed states that block only some later updates instead of all downgrades, retries, duplicate submissions, or aggregate-state mutations
- comments that refer to one coordinate while the code keys data by another
- role-dependent thresholds routed through generic queues
- state replacement that does not invalidate derived or cached state
- request IDs, session IDs, or operation IDs stored globally instead of per in-flight object
- merge or eviction logic that can evict the object currently being traversed
- cached checkpoint, request, config, or game state reused on retry without revalidation against current authoritative state
- one-time scan watermarks or "already seen" markers on objects whose classification can legitimately change later
- policies enforced at wake-up or signaling boundaries but not at the underlying provider or write sink
- append-only histories stored as mutable read-modify-write objects under concurrent writers instead of immutable write-once records
- fallback paths that do not preserve enough state to transition cleanly into the alternate recovery mode
- event, listener, subscription, or gossip paths where a policy bit is checked at admission but dropped before delivery
- fork, reorg, retry, failed-prewarm, abort, or recovery paths that reuse caches from a prior parent hash, verifier state, peer state, or execution context
- rollback paths in authenticated or persisted state that restore a nearby object but not the exact mutated coordinate
- invalid, syncing, timeout, empty-response, and already-known states that update state in one path but not the analogous path
- parent operations that queue or spawn protocol-generated child work, where failure or filtering of the child should rewind the parent group but the code only drops the child result
- round, epoch, or session scoped privileged work queues where enqueue, wake-up, dequeue, and replay use different freshness or authorization sources

Questions to answer:
1. What are the legal states and transitions?
2. Which fields are derived from those states and must be reset on transition?
3. Are all transition paths symmetric?
4. Are roles, indices, heights, epochs, rounds, views, checkpoints, and handoffs scoped consistently?
5. Can stale state cause later enforcement, verification, or feedback to apply to the wrong object?
6. Is object reuse revalidated against the current authoritative state before it influences a new decision?
7. Is the policy enforced where the object is actually read, written, or executed?
8. If a parent operation generates child work, what is the atomicity boundary: parent only, child only, or the whole group?
9. Are queue wake-up, dequeue, and replay paths revalidating the same round, epoch, finalized boundary, or authorization state that admission checked?

Severity guidance:
- Medium for stale-state liveness or integrity issues.
- High only if stale state can authorize privileged actions, misapply bridge or validator actions, or cause broad consensus corruption.
```
