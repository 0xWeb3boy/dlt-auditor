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
- comments that refer to one coordinate while the code keys data by another
- role-dependent thresholds routed through generic queues
- state replacement that does not invalidate derived or cached state
- request IDs, session IDs, or operation IDs stored globally instead of per in-flight object
- merge or eviction logic that can evict the object currently being traversed

Questions to answer:
1. What are the legal states and transitions?
2. Which fields are derived from those states and must be reset on transition?
3. Are all transition paths symmetric?
4. Are roles, indices, heights, epochs, rounds, views, checkpoints, and handoffs scoped consistently?
5. Can stale state cause later enforcement, verification, or feedback to apply to the wrong object?

Severity guidance:
- Medium for stale-state liveness or integrity issues.
- High only if stale state can authorize privileged actions, misapply bridge or validator actions, or cause broad consensus corruption.
```
