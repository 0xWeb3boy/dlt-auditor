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
