# Prompt Family: Authoritative State And Boundary Enforcement

## Use This For

- Cached state reused without rechecking authoritative on-chain or canonical state.
- Local config accepted where live registry, contract, or protocol state should govern.
- Policies enforced in watcher, helper, scheduler, or builder layers but not at the actual provider, executor, or storage sink.
- Decisions made from proxy invariants instead of the authoritative state that defines correctness.
- Fork, checkpoint, head, or safe-head rules applied in one construction path but omitted in another equivalent path.

## Prompt

```text
Hunt for authority and enforcement-boundary bugs in a blockchain or DLT codebase.

Focus on decisions that depend on current chain, contract, registry, fork, head, safe-head, finalized, checkpoint, or policy state, especially when the code also has caches, local config, derived mirrors, watch channels, or helper-layer summaries.

Prioritize:
- proposer, challenger, sequencer, validator, and retry flows
- watcher/provider pairs
- env or config builders
- registry and policy queries
- storage write paths and append-only history code

Search patterns:
- cached or existing requests reused by structural match alone
- local config accepted without checking live on-chain or canonical policy state
- policy enforced in watcher, scheduler, helper, or builder code but not in the provider, executor, or writer that actually uses the data
- duplicated constructors where one path applies a fork or policy gate and another builds the same object inline without it
- raw, original, canonical, or node-authoritative artifacts being replaced by transformed, mirrored, decrypted, cached, helper-produced, or proof-carried equivalents before the sink
- tooling or verification flows where caller-supplied or proof-supplied artifacts can override the locally trusted verifier, registry, config, or asset set
- decisions that depend on externally defined values such as fee, pricing, registry, or policy signals, but use local recomputation or helper-derived values instead of the protocol-authoritative source
- decisions based on proxy values like output-root equality, metadata hashes, request shape, or status flags instead of the authoritative state that defines correctness
- state, overlay, provider, or cache lookups keyed by height, range, current head, or implicit context where the authoritative identity is a block hash, root, parent, fork, or target tuple
- helper-produced fork filters, protocol statuses, checkpoints, or derived roots built from separate source inputs that should come from one authoritative snapshot
- proof-carried or caller-supplied artifacts that can replace the locally authoritative verifier, root, target, fork, or state source at the sink
- canonicality checks that rely on transient indices when persisted canonical state is the source of truth
- read-only, debug, witness, trace, or inspection flows that reuse normal execution or import helpers and may still reach persistent writers unless write suppression is enforced at the actual sink
- chain-variant or rollup adapters that reuse base-client pools, signers, state journals, gas meters, or block import helpers while adding variant-specific authority such as sequencer policy, delayed-message accumulators, module roots, or generated transactions
- runtime artifact loaders where `latest`, default, local cache, directory default, or config shorthand is accepted before comparing the measured module, root, version, fork, or genesis identity against the chain, challenge, validator, or verifier expectation
- validator or sequencer progress stores keyed by height, count, local read progress, or optional reader state where the authoritative identity includes block hash, accumulator, finalized boundary, module root, or delayed-message sequence
- extraction or validation subsystems that key cleanup, retention, or early-return logic by local read progress, cache occupancy, or processed counters when the authoritative boundary is finalized, safe, validated, or on-chain state
- witness, log, preimage, or payload recording paths that are best-effort, optional, or split across modes even though later validation or sequencing treats the recorded data as mandatory
- privileged admission paths that check current authorization in one layer, but dequeue, replay, or execution paths consult a cache, mirror, watch channel, or stale local summary instead of the same authoritative source
- range, root, proof, log, or aggregate APIs that compute for `[start,end]` or another explicit target but validate cache freshness, reorg stability, or canonicality against current head, latest state, or a nearby proxy instead of the target block hash/root/range tuple
- external consensus, checkpoint, milestone, or validator-set data selected by timestamp, latest state, local cache, or retry fallback where all validators must instead derive the same snapshot identity before local execution consumes it
- helper APIs that answer "who owns this?" or "is this accessible?" from a cache, object ref, prior effects, or partial store view. Treat those answers as hints unless the sink rebinds them to current canonical state before mutation

Questions to answer:
1. What source is authoritative for this decision right now?
2. Is that source re-read or revalidated at the point of use?
3. Could cached or local state remain plausible after authoritative state changed?
4. Is the rule enforced in every path that constructs or consumes the object?
5. Is the code comparing the real governing state, or only a proxy for it?
6. Is the code using the authoritative artifact or source at the actual sink, or only in an earlier watcher, helper, builder, or validation layer?
7. If the path is supposed to be read-only, where is persistence actually prevented: in the wrapper, in the shared helper, or at the storage sink itself?
8. If the decision depends on a loaded artifact, verifier context, or tracker state, where is the measured or live authoritative identity compared to the expected identity before the sensitive sink?
9. If cleanup or reuse depends on progress, is the progress boundary merely local processing state, or is it tied to finalized, validated, or otherwise authoritative protocol state?
10. If this code extends a base client, which layer is authoritative for the variant-specific fact, and is that fact rechecked at the shared base-client sink?

Severity guidance:
- Medium by default for stale-policy, stale-checkpoint, sink-coverage, and proxy-state bugs.
- High if stale or proxy state can affect consensus-sensitive acceptance, dispute handling, privileged actions, or finalized-state integrity.
```
