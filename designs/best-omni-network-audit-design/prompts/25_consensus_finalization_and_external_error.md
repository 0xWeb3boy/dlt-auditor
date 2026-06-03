# Consensus Finalization And External Error

## Family Objective

Find consensus, block-import, finalization, and Engine/API bugs where deterministic state transitions depend on non-deterministic helper work, misclassified external errors, or fork-versioned side arguments that are not bound to the payload being accepted.

## Hunt Steps

1. Enumerate consensus-critical callbacks and sinks: proposal build, proposal verify, block import, finalization, vote-extension verify, forkchoice/head update, state-root or app-hash update, and generated system work.
2. For each callback, list all external or locally non-deterministic dependencies: RPC calls, execution-client calls, snapshot/sync state, filesystem/config reads, background builders, wall-clock state, peer/network state, and caches.
3. Check whether errors from observer/helper/background work are propagated into deterministic consensus results. Non-deterministic availability failures should not halt or diverge finalization unless they are part of deterministic block input.
4. Inspect retry loops. Split errors into transient transport/local availability, deterministic invalid input, unsupported method or fork field, authorization failure, malformed payload, and node sync state. Retrying all errors in proposal validation or finalization is high signal.
5. Build a payload side-argument matrix for Engine API, block import, forkchoice, or execution APIs. Compare payload-contained fields against side arguments such as roots, sidecars, hashes, commitments, optional fork fields, withdrawals, method version, chain variant, and timestamp/fork gates.
6. Search for "empty", "nil", default, cached, or independently supplied side arguments next to payloads that may contain matching non-empty fields.
7. Compare local proposer/build checks to non-proposer validation and finalization checks. The non-proposer path must reject unsupported or inconsistent payloads without entering infinite retry or committing partial side effects.
8. For optimistic/background build modes, verify that build failures, cache misses, and local node availability cannot affect deterministic finalization of an already-decided block.
9. Treat local availability as a consensus issue when its error escapes a replicated callback. A local RPC, sync, snapshot, filesystem, cache, or background-builder failure can still be serious if honest nodes can observe different local conditions while processing the same decided input.
10. For every "retry forever", "retry until ok", "will retry", or unknown-status loop, design the smallest proof: a mocked deterministic invalid-input error, an unsupported-method error, an authorization error, a malformed-response error, and a transient transport error. The first four should usually reject or fail closed rather than retry like transport.
11. When a payload producer returns an envelope plus detached sidecars, compare the producer's full output to the validator/importer's full input. Check both missing sidecars for present payload features and non-empty sidecars for payloads that should not have them.
12. Build an error escape table for every callback. Columns: dependency, error class, whether the error is deterministic for the block input, whether honest nodes may differ, where the error is caught, and what the consensus caller observes.
13. Do not collapse "local" and "optional" together. Optional work may still be dangerous if it runs synchronously inside a replicated callback and its failure changes the callback return value.
14. For malformed or unsupported payloads, prove whether rejection is immediate and deterministic. If the application retries until context cancellation, record what the consensus engine does while waiting and whether the same proposal will be retried in later rounds.
15. For detached-data transaction types, build an end-to-end sidecar table. Include transaction admission, builder payload creation, block-body storage, proposal serialization, validator extraction, execution/import method version, side arguments, and dependency error classification. Treat empty or default side arguments as high signal only when the payload can require non-empty side data.
16. When dependency behavior is uncertain, use a local mock or source inspection to classify application behavior independently. A mocked deterministic invalid-input or unsupported-fork error is enough to prove whether the application retries, rejects, accepts, or leaks the error through a consensus callback.
17. Preserve local-helper finalization issues when the helper runs synchronously inside a replicated callback. A helper may be optional from a product perspective but consensus-critical if its error is returned before the callback result is accepted.

## Candidate Requirements

For every candidate, include:

- deterministic callback or consensus sink;
- non-deterministic dependency or misclassified error;
- exact payload field or side argument mismatch, if applicable;
- detached-data or sidecar preservation table, if applicable;
- why honest nodes can diverge, halt, or retry forever;
- what compensating checks exist in proposer, verifier, finalizer, and execution client paths;
- a focused test that would confirm or kill the issue.
- if live dependency behavior is uncertain, the mock or harness that would prove the application's classification behavior.
- an error-class table showing deterministic invalid input, malformed dependency response, unsupported fork/method, transient transport, local availability, and optional background failures separately.

## False-Positive Controls

- Do not report ordinary local node downtime unless the code propagates it through a deterministic consensus callback.
- Do not report a side-argument mismatch if the execution client deterministically rejects it and the application handles that rejection by rejecting the proposal rather than retrying forever.
- Treat background optimizations as low severity unless their errors escape into consensus state transitions.
- Do not downgrade a deterministic-callback error solely because it is "local"; first prove that the error is swallowed, isolated from consensus output, or identical across honest nodes.
