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
- Proof builders that return an empty proof for absence instead of explicit empty-root or non-existence evidence.
- Pruning or compression that changes node representation without invalidating revealed paths, proof caches, or derived metadata.
- Mutate-then-validate flows in authenticated trees where rollback may not restore the exact node, subtrie, path, or account that was changed.
- Canonical persistence paths that assume trie updates, state diffs, or derived roots exist for fork ancestry instead of detecting and recomputing missing data.
- Sidechain or fork-local hash reconstruction keyed by height instead of block hash and parent relation.
- Error results ignored or logged-only in canonicalization, persistence, or state-root paths.
- Transient touched, exists, empty, dirty, or journaled flags that affect commitment or clearing semantics but are not reverted symmetrically on rollback or failed execution.

Questions to answer:
1. What object is authoritative: block hash, state root, trie node, proof, checkpoint target, canonical DB state, or in-memory overlay?
2. Is every derived object bound to that authority before it is reused?
3. If the code resumes, prunes, rolls back, or switches forks, which cached or derived data must be invalidated?
4. Can an absence proof be distinguished from missing proof material?
5. Are mutations atomic, or can failed validation leave a partially modified authenticated state?
6. Does persistence fail closed when required derived state is missing?
7. If account or object liveness is tracked through transient flags, are those flags journaled and reverted with the same authority as the committed state?

Severity guidance:
- High if a malformed proof or state root can be accepted by another trust domain, bridge, light client, or consensus path.
- Medium for state-integrity hardening where proof, trie, cache, or persistence correctness is improved but exploitability is not proven.
- Low for offline maintenance tools with no production trust boundary.
```
