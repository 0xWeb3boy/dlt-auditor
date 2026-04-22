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

Questions to answer:
1. What source is authoritative for this decision right now?
2. Is that source re-read or revalidated at the point of use?
3. Could cached or local state remain plausible after authoritative state changed?
4. Is the rule enforced in every path that constructs or consumes the object?
5. Is the code comparing the real governing state, or only a proxy for it?
6. Is the code using the authoritative artifact or source at the actual sink, or only in an earlier watcher, helper, builder, or validation layer?

Severity guidance:
- Medium by default for stale-policy, stale-checkpoint, sink-coverage, and proxy-state bugs.
- High if stale or proxy state can affect consensus-sensitive acceptance, dispute handling, privileged actions, or finalized-state integrity.
```
