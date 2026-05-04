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
- Program, contract, VM, or proof systems that cache call counts, recursion depth, finalize cost, constraint counts, proof cost, or verifier metadata. Recompute or revalidate from the current graph or artifact at admission and final execution.
- User-supplied or artifact-supplied resource metadata that is aggregated with ordinary arithmetic. Use checked arithmetic and reject before the value reaches fee, quota, proof, or deployment acceptance.
- Recursive semantic validators where each nested parse, call, or function expansion must share one authoritative budget and maximum-depth policy.
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
- admission, scheduling, and execution paths that meter different resource dimensions for the same operation, such as execution units vs loaded-account-data cost, trace growth vs stack depth, or declared frame size vs actual receive-buffer capacity
- cleanup or truncation paths that use a weaker predicate than insertion/admission paths
- cache-hit paths that return stored execution or precompile result objects containing gas, quota, reservoir, refund, or caller-local accounting state
- batch-mode decisions that choose clean, incremental, bounded, or unbounded work based only on the next local window instead of the full remaining range
- shared sender, authority, account, or reservation handles enforced in one pool, queue, or subpool but not in the others that consume the same underlying resource
- cross-language, cross-process, or offloaded execution APIs that receive a mutable budget, gas, or quota on entry but do not return the remaining budget to the authoritative charging layer
- recovery or trap-handling paths that retry with larger stacks, buffers, or allocations without a one-time guard, context restriction, or outer quota
- parent operations that spawn derived work where the parent is charged, finalized, or committed before the child work proves cleanly met the same accounting or filter rules
- RPC, query, historical-range, log, trace, fee-history, proof, or witness APIs where total work is the product of a range and caller-supplied per-item options. Cap every dimension before spawning goroutines, allocating result matrices, building cache keys, or entering stored-filter replay, chain-specific variants, symbolic latest/pending/finalized selectors, or helper paths that construct the same expensive query.
- GraphQL, REST, or query APIs whose cost formulas combine page size, storage reads, and child selection complexity. Check that caller-controlled first, last, range, or page-size values multiply every per-item storage and nested resolver cost, not only child complexity.
- Simulation, dry-run, tx selection, and final execution paths that enforce the same resource dimension in different places. Compare declared max gas, actual max gas, serialized byte size, aggregate block limits, and executor accounting.
- transaction pools with multiple subpools, delegated senders, blob/sidecar data, replacement rules, or feature-specific transaction types. Check that sender-level and resource-level isolation is enforced consistently across every subpool, not only the legacy pool.
- offloaded or cross-runtime execution that receives a mutable gas, quota, or multi-resource budget. The caller's authoritative meter must receive the post-call remaining budget and burn the consumed amount before state activation or persistence.
- background verification, sync-maintenance, pruning, and repair loops that derive their work window from current head minus a checkpoint, milestone, or finalized boundary. Check that the trusted boundary is fresh, the window is capped before materializing work, and missing boundary data disables or defers the loop instead of scanning an unbounded range
- transaction types that auto-create trust lines, holdings, directories, tickets, delegate objects, shares, receipts, or other state entries as a side effect. Check that reserve, owner-count, spam-cost, and quota accounting is enforced before the auto-created object reaches durable state
- failed protocol handshakes, upgrades, peer sessions, or admission attempts where resource or session accounting is allocated before verification. Rejection paths must release or charge the same resource state as successful handoff paths
- traffic-control, rate-limit, spam-weight, or peer-penalty systems where only successful submissions are attributed. Invalid, duplicate, rejected, timeout, already-known, and consensus-output paths should update resource or accounting state symmetrically when they consume comparable work
- transaction or message resubmission caches where the key is a digest, object ID, sender, peer, or client address. Check that all ingress paths propagate the same attribution key and that paths without attribution cannot bypass the limiter
- consensus proposal builders and consensus verifiers that enforce related limits independently. Count, byte, per-item, aggregate-byte, recursion-depth, and per-author limits must match between production and validation, with any-limit-exceeded rejection rather than partial enforcement
- counters, sizes, or quotas derived from protocol state that use ordinary addition, subtraction, or narrowing where saturation, checked arithmetic, or explicit rejection is required. Overflow or narrowing must not turn an over-limit condition into apparent progress or admissibility
- lifecycle-triggered contract execution, precompile execution, and block hook callbacks that swap gas meters, temporary stores, or execution contexts. The temporary meter must inherit the parent bound, and expected out-of-gas errors should fail closed without hiding unexpected panics
- precompile or host-call paths that accept caller gas limits but do not add subcall overhead, cleanup cost, callback cost, proof-size base cost, or refund accounting before accepting work.
- simulation, trace, estimate, runtime API, or debug execution paths that manually reconstruct transaction size, proof cost, access lists, authorization lists, or fee fields instead of using the canonical transaction/accounting representation used by live execution.
- long-lived subscriptions, listeners, peer maps, and stream state where the allocation or registration point is separate from config parsing. Enforce limits under the same lock or reservation policy that mutates the retained collection
- resource-limit or cost-exceeded errors nested inside multiple execution-result variants, such as processed, skipped, aborted, replayed, simulated, prechecked, or partially applied outcomes. Every variant that consumed or attempted bounded work must classify limit exhaustion consistently.
- recursive parsers, type constructors, or semantic validators that accept an optional cost, gas, quota, or budget object. Check that every nested parse or validation call receives and updates the same authoritative meter.
- decoders for untrusted transaction, block, receipt, proof, or query objects that fully decode variable-length lists before enforcing protocol count limits. Treat decode-time cardinality as a resource boundary: count raw items, cap every list dimension, and reject before per-item allocation or nested decoding.

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
12. Is the true cost a single scalar, or does it multiply across range length, requested percentiles/options, sidecar count, delegated sender state, or offloaded runtime work?

Severity guidance:
- Medium by default for DoS, fee bypass, and resource exhaustion.
- Raise only if the missing limit can destabilize consensus, settlement, bridge processing, or systematically underprice privileged operations.
```
