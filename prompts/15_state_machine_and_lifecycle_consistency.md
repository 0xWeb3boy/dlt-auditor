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
- transitions from non-leader to leader, pre-finalize to finalize, success to failure, or live to replay mode where continuity state such as ticks, roots, nonce state, reservation counters, or snapshot handles is updated on one path but not the others
- request IDs, session IDs, or operation IDs stored globally instead of per in-flight object
- merge or eviction logic that can evict the object currently being traversed
- cached checkpoint, request, config, or game state reused on retry without revalidation against current authoritative state
- one-time scan watermarks or "already seen" markers on objects whose classification can legitimately change later
- policies enforced at wake-up or signaling boundaries but not at the underlying provider or write sink
- startup and sync-completion paths should not initialize stronger safety labels from weaker local state. Check whether unsafe, optimistic, pending, syncing, safe, finalized, or cross-domain-safe labels are copied, zeroed, or defaulted during recovery
- if a component once observed a synced, finalized, or ready state, later responses that regress to syncing, unknown, or invalid should be classified explicitly rather than treated as ordinary progress
- shared controller state that drives forkchoice, reorg, reset, or retry decisions should be read under one coherent lock/snapshot; mixed old/new fields can create impossible lifecycle transitions
- append-only histories stored as mutable read-modify-write objects under concurrent writers instead of immutable write-once records
- fallback paths that do not preserve enough state to transition cleanly into the alternate recovery mode
- event, listener, subscription, or gossip paths where a policy bit is checked at admission but dropped before delivery
- fork, reorg, retry, failed-prewarm, abort, or recovery paths that reuse caches from a prior parent hash, verifier state, peer state, or execution context
- rollback paths in authenticated or persisted state that restore a nearby object but not the exact mutated coordinate
- invalid, syncing, timeout, empty-response, and already-known states that update state in one path but not the analogous path
- paths that validate authority, reserve state, or prepared state early but persist the authoritative result only on success, leaving failure, replay, or abort paths with stale lifecycle, nonce, or replay state
- parent operations that queue or spawn protocol-generated child work, where failure or filtering of the child should rewind the parent group but the code only drops the child result
- round, epoch, or session scoped privileged work queues where enqueue, wake-up, dequeue, and replay use different freshness or authorization sources
- startup, constructor, and background-maintenance paths that initialize security-sensitive loops from persisted state. Oversized, stale, impossible, or fork-incompatible persisted values should be sanitized or rejected before they drive reorg, milestone, sync, verifier, or peer-churn decisions
- finalization, replay, and recovery paths where internally generated protocol work must remain grouped with the parent block or operation; dropping, filtering, or failing the generated work should rewind or reject the whole group when that is the consensus rule
- equivalent transition paths for the same range-based protocol object, such as direct message handling, side-vote handling, post-consensus handling, replay, recovery, bridge submission, and buffer flushing, where one path enforces exact successor continuity or fail-closed storage errors and another path only enforces freshness or overlap prevention
- locally executed, speculatively executed, or peer-fetched work that is later excluded from the finalized checkpoint, block, batch, or epoch boundary. Finalization must rollback, quarantine, or prove isolation of those effects before durable state can be served or reused
- in-memory consensus, batching, congestion, or timing state that is reconstructed by replay after restart. If replay reconstructs only a fixed window, check that the committed digest or snapshot covers exactly the state retained across live execution and recovery
- epoch, checkpoint, or committee transitions where old-epoch messages can arrive while new-epoch state is being initialized. Verify that readiness, signer set, traffic counters, and pending work are fenced by one coherent transition state
- event ingestion, bridge watcher, withdrawal finalizer, inbox, outbox, receipt, or log-processing watermarks keyed by only block, height, batch, timestamp, or max-seen aggregate when the source can contain multiple distinct relevant events at that coordinate. Duplicate guards should use the full event identity and ordering key required by the source chain
- state machines that wait for progress on an object that can never fit, complete, or become valid under the current local capacity or configuration. Fail closed or tear down the object instead of suppressing forever
- asynchronous validation, approval, signing, vote, or proposal results that are queued and later applied after the node's fork view, reward cycle, signer set, accepted block, or local validation state may have changed. Revalidate freshness at the sink, not only when the work was queued.
- caches keyed by a digest, block hash, message hash, or object ID when the real identity also includes epoch, reward cycle, round, view, fork, signer set, or lifecycle phase. Cache hits must be scoped by every coordinate that can change the meaning of the object.
- Reconciliation or recovery logic backed by external durable stores, caches, or replicated service state. Read failure, timeout, unknown state, and empty state must remain distinct before leader election, block production, failover, or repair decisions.
- Quorum, vote, or reconciliation maps keyed by metadata that can vary across replicas. Group by canonical protocol identity, and use epoch, timestamp, retry count, or promotion metadata only as scoped tie-breaker data when the protocol permits it.
- Async worker, retry, or fanout clones that inherit ownership-sensitive guards, leases, cancellation handles, or drop-time cleanup state. Worker lifetime must not extend logical ownership or suppress cleanup or failover.

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
10. Does every "already processed" or progress watermark use the same identity granularity as the source event stream: block plus transaction, log, or event index where multiple events can share a block?

Severity guidance:
- Medium for stale-state liveness or integrity issues.
- High only if stale state can authorize privileged actions, misapply bridge or validator actions, or cause broad consensus corruption.
```
