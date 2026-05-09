# Prompt: Base Hunter

Use this after `00_protocol_mapper.md` and together with one family prompt from `prompts/`.

## Objective

Find candidate issues of the requested family in the current blockchain or DLT codebase.

## Prompt

```text
You are hunting for one specific family of security issues in a blockchain or DLT codebase.

Inputs you already have:
- A protocol map of the system.
- One issue-family prompt describing what to look for.

Your task:
1. Enumerate the most relevant code paths for that family.
2. Search for places where the intended invariant is checked in some paths but missing in others.
3. Compare admission-time checks, execution-time checks, simulation paths, recovery paths, timeout paths, cleanup paths, and upgrade or migration paths where relevant.
3a. For transaction, block, message, and proof admission, build an ingress-to-sink matrix. For each object type, list every path that can place it into the shared sink: RPC, gossip, local builder, forced/internal insertion, replay/recovery, block packing, manager verification, and block verification. Mark which paths are trusted bypasses and which are untrusted. Every untrusted path should run the same policy, resource, context, and protocol-message checks before the object reaches the shared sink.
4. Identify suspicious asymmetries, TODO-style comments, placeholder checks, broad membership checks, stale state reuse, or checks performed too late.
5. Search for decisions that rely on cached, mirrored, or locally configured state instead of revalidating against authoritative chain or contract state at the point of use.
6. Search for policies enforced in signal, watcher, helper, or builder code but not in the provider, constructor, execution path, or storage write path that actually consumes the data.
7. Search for decisions keyed by one protocol coordinate, index, root, nonce, height, or game state while the code validates a broader aggregate, a proxy, or the first mismatch.
8. Produce at most 5 candidate findings, ranked by likelihood.
9. Search for the same semantic value carried in two or more representations, where only one representation is validated, canonicalized, or trusted.
10. Search compatibility, migration, mode-specific, and legacy branches for weaker hashing, version derivation, source selection, or verification behavior than the main path.
11. Search for sinks that should recompute an identifier, hash, version, capability, or selector from authoritative parsed state, but instead trust a detached field, helper output, cache entry, proof-carried value, or caller-supplied metadata.
12. Compare every special-case, compatibility, replay, migration, benchmark, recovery, sidechain, and fork-specific path against the normal validation path. Ask whether it skips only the exact non-comparable field or accidentally skips core identity, parent, root, accounting, authorization, or policy checks.
13. Search for feedback loops where untrusted peer, transaction, or proof outcomes should update reputation, penalties, scheduling, listener filtering, cache invalidation, or cleanup state. Check whether success, empty, invalid, timeout, abort, and retry paths update that state symmetrically.
14. Search for cached execution, proof, or state-provider outputs that include invocation-local state. On cache hits, the code should rebind or reconstruct caller-local accounting, fork identity, verifier context, and authoritative state instead of cloning stale composite objects.
14a. Search cached validation artifacts that cross rule-version, fork, epoch, consensus-parameter, or feature-gate boundaries. A cached "checked" object should carry the exact rule context that produced it, and sinks should revalidate when the current context differs.
15. In peer-driven paths, compare identity checks against context checks. Ask whether the code validates only a hash, type, peer, or object ID, or also validates the expected parent, predecessor, request token, chain segment, fork context, or authoritative metadata that makes the response meaningful.
16. Search read-only, debug, witness, trace, simulation, and inspection flows that reuse normal execution, import, or persistence helpers. Check whether writes are disabled at the actual storage or canonical-state sink, not just by a wrapper flag.
17. Compare constructor and startup paths for security-sensitive dependencies against steady-state enforcement paths. Ask whether verifier, signer, runtime-artifact, tracker, or state-provider initialization can fail open, fall back to trust mode, or proceed with incomplete chain context.
18. For multi-stage pipelines, compare extraction, witness recording, validation, pruning, recovery, and live execution. Ask whether later stages assume a witness, accumulator, module root, finalized boundary, or sequence check that earlier stages only record best-effort or under a different progress predicate.
18a. For proof or circuit-backed transaction families, build a per-field comparison across transaction object, signed message, witness, public data, circuit constraints, and persisted state. Search for fields that are present in execution or public data but not constrained equal to the signed or committed representation.
19. Search for internally generated or cascaded work that should be grouped atomically with its parent operation, such as retryables, auto-redeems, generated proofs, queued privileged submissions, or background follow-on actions. Check whether failure, filtering, replay, or recovery drops only the child work while keeping the parent side effects.
20. Search for privileged queues or session-bound workers where admission uses one authorization or freshness source but dequeue, replay, or round-transition execution uses another, such as cached controller maps, helper summaries, or stale progress state.
20a. For internal service APIs, compare security objects that are constructed with the route tree or server builder that actually handles requests. Treat "validator exists nearby" as insufficient unless middleware, interceptors, or handlers are mounted on every sensitive route.
20b. For nonce, sequence, ticket, or replay-sensitive admission paths, compare committed-state checks against local pending, in-flight, reserved, or recently-used state. Ask whether local state is used only to reject stale or duplicate work, or whether it can accidentally widen a future acceptance window.
20c. For verifier, prevalidator, middleware, signer-scope, or policy objects, compare construction with actual route, stream, queue, or sink enforcement. Treat optional policy configuration as suspicious if disabling the policy also disables baseline validation.
21. For account-ledger systems, build a before/after accounting model for each transaction family: direct entries, generated entries, reserves, owner counts, fees, supply, shares, receipts, obligations, and invariant finalizers.
22. For delegated, granular, or feature-scoped authorization systems, compare the permission object to the exact executed transaction shape, asset or domain, receiver policy, and every generated side effect.
23. For proposal/validation consensus systems, map proposal identity, prior-ledger binding, transaction-set or payload ordering, validator or committee trust, quorum arithmetic, and wrong-ledger, catch-up, or round-transition modes before searching for missing checks.
24. Compare adapter entrypoints against their canonical native entrypoints. For every precompile, cross-runtime query helper, legacy RPC adapter, or compatibility transaction path, ask whether it reuses the same validation, address association, chain or replay domain, message type, and final sink as the native path.
24a. For precompiles, host functions, proxy bridges, and VM-to-native adapters, compare caller class, target class, selector family, and call mode. Treat "same address format" as insufficient: distinguish EOA, contract-with-code, precompile, delegated/proxy real account, and native account. Search for broad generic dispatch adapters, allow-all proxy types, selector checks that run after dispatch setup, and target filters that check code presence but not precompile membership or native policy.
25. Search for early side effects that are recorded before final admission or success: pending nonces, peer penalties, callback writes, accounting deltas, generated receipts, cached proposal blocks, and temporary store writes. Check whether every later rejection, timeout, panic, or failed acknowledgement rolls them back or avoids recording them until acceptance.
25a. For delayed-accounting pipelines, build a before/after model around the exact state that later admission reads. Accepted transactions, votes, spends, withdrawals, account locks, and generated obligations should reserve or mutate the authoritative accounting state before another equivalent object can pass a stale check.
26. In consensus and p2p lifecycles, compare the predicate that verifies an object with the predicate that later mutates state from it. A certificate, peer response, stream discriminator, or proposal that was not needed or verified for the current transition must not still drive stored state, emitted votes, or allocation.
27. Search caller/callee contract edges, not just protocol invariants. Compare what helpers, parsers, VM syscalls, copy-back routines, and cryptographic decoders document as their required backing span, output-buffer size, ownership lifetime, and exact destination-length contract against what call sites actually provide.
28. Treat typed stack locals, missing sentinel bytes, escaped local metadata, fixed-capacity receive buffers, and post-execution memcpy or copy-back without exact length equality as high-signal candidates.
29. Search admission and finalization paths where a policy is enforced against one representation while the final state mutation consumes another. Compare input fields vs emitted outputs, serialized rejected effects vs recomputed execution effects, cached resource metadata vs live call graphs, and deployment metadata vs synthesized proof or verifier artifacts.
30. Search privileged proxy, gateway, and service APIs for fallback behavior. Unknown methods, routes, selectors, or operation names should fail closed unless explicitly allowlisted; blacklist filtering is high-signal when the upstream target exposes a broader surface.

For each candidate include:
- Title
- File and function
- What invariant seems intended
- Why the current path may violate it
- Attacker preconditions
- Possible impact
- What evidence would confirm or kill the hypothesis

Constraints:
- Do not claim a vulnerability just because a similar historical bug existed elsewhere.
- Prefer concrete code-level reasoning over speculation.
- Treat cryptographic validity, authorization, freshness, replay protection, version gating, and resource metering as separate properties.
- If no solid candidates exist, say so clearly.
```
