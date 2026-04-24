# Prompt Family: Authenticated State, Proof, And Persistence Integrity

## Use This For

- Merkle, MPT, sparse trie, accumulator, commitment tree, state-root, and proof generation code.
- Canonical persistence, checkpoint resume, state rebuild, pruning, static-file handoff, and rollback paths.
- Fork-aware state providers, overlays, caches, prewarm state, and derived trie updates.
- Light-client, bridge, RPC, or internal proof APIs that return inclusion or non-existence evidence.

## Prompt

```text
Hunt for bugs where authenticated state, proof material, or derived persistence data can become incomplete, stale, misbound, or non-atomic.

Focus on data that is derived from canonical state but later treated as authoritative: roots, proofs, revealed paths, trie updates, overlays, checkpoints, state-provider caches, fork-local hash views, and persisted ranges.

Search patterns:
- Checkpoints or resumable rebuild state that are not bound to the target range, root, block hash, fork, or table set they resume.
- State overlays, providers, or caches keyed by block number, range, or implicit current head where competing forks can share that coordinate.
- In rollup or cross-chain supervisors, inspect persisted source/derived block pairs. Reorg, reset, rewind, and frontier-advance paths should bind both sides of the pair by hash, number, parent, timestamp, and canonical source status before promoting or deleting state.
- Proof builders that return an empty proof for absence instead of explicit empty-root or non-existence evidence.
- Pruning or compression that changes node representation without invalidating revealed paths, proof caches, or derived metadata.
- Mutate-then-validate flows in authenticated trees where rollback may not restore the exact node, subtrie, path, or account that was changed.
- Canonical persistence paths that assume trie updates, state diffs, or derived roots exist for fork ancestry instead of detecting and recomputing missing data.
- Append-only proof, trie, log, or witness stores should reject new entries unless they extend the stored tip or fall within an initialized proof window. Missing windows, unknown exact versions, or replacement outside the earliest/latest range should fail closed.
- Reset anchors and recovery checkpoints should be revalidated against the current canonical source chain at reset time, not only when they were first recorded.
- Sidechain or fork-local hash reconstruction keyed by height instead of block hash and parent relation.
- Error results ignored or logged-only in canonicalization, persistence, or state-root paths.
- Transient touched, exists, empty, dirty, or journaled flags that affect commitment or clearing semantics but are not reverted symmetrically on rollback or failed execution.
- proof, challenge, or validator-state builders that derive indices, message counts, or fallback states from local counters, parent objects, or latest aliases instead of authoritative batch metadata, challenge metadata, or explicit boundary-state objects
- proof-support pipelines where preimages, logs, receipts, tx indexes, or other witness material are recorded only on some modes or ignored on error even though later validation requires them
- challenge or proof helpers that return booleans, generic success, or loosely scoped objects where the caller really needs the concrete fallback state, module root, or challenged object that governs the proof
- resume or recovery code that binds cached or persisted validation state to height alone when the authoritative identity includes hash, root, finalized boundary, module root, or challenged assertion identity
- state, receipt, log, root, witness, or proof helpers that are parameterized by a range, block number, page number, or requested key but only validate the returned data against current head, total count, local cache state, or malformed-but-plausible pagination metadata
- content-addressed, page-addressed, or key-addressed peer payloads where both the payload hash/key and the page/order metadata must be recomputed and checked before storing, scheduling follow-up requests, or reporting completion

Questions to answer:
1. What object is authoritative: block hash, state root, trie node, proof, checkpoint target, canonical DB state, or in-memory overlay?
2. Is every derived object bound to that authority before it is reused?
3. If the code resumes, prunes, rolls back, or switches forks, which cached or derived data must be invalidated?
4. Can an absence proof be distinguished from missing proof material?
5. Are mutations atomic, or can failed validation leave a partially modified authenticated state?
6. Does persistence fail closed when required derived state is missing?
7. If account or object liveness is tracked through transient flags, are those flags journaled and reverted with the same authority as the committed state?
8. If the sink needs a specific challenged object, batch boundary, module root, or fallback state, does the helper return that exact object, or only a hint that lets the caller guess?
9. Are all witnesses needed for later proof or validation recorded fail-closed at the time they are first observed, or can the system advance after a recording failure and only discover the gap later?

Severity guidance:
- High if a malformed proof or state root can be accepted by another trust domain, bridge, light client, or consensus path.
- Medium for state-integrity hardening where proof, trie, cache, or persistence correctness is improved but exploitability is not proven.
- Low for offline maintenance tools with no production trust boundary.
```
