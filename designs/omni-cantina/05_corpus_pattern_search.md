# Prompt: Corpus Pattern Search

Use this after `00_protocol_mapper.md` and before or alongside the family scans.

## Objective

Use the structured vulnerability corpus as a search layer to retrieve similar historical patterns, turn their motifs into target-repo searches, and produce concrete hypotheses for later validation.

## Prompt

```text
You are running the corpus-search phase for a blockchain or DLT audit.

Your job is not to claim that historical bugs exist in the target repo. Your job is to use corpus records and retrieval cards as pattern generators, then inspect the target code for concrete evidence.

Inputs:
- The target repo.
- The filled `repo-context.md`.
- The filled or seeded `feature-coverage.md`.
- The shared corpus under `/testing/dlt-auditor/corpus/imports`.
- The corpus search tool in this design: `bin/search-corpus`.

Step 1: Build focused corpus queries.
- Use the protocol map to derive queries from:
  - trust boundaries,
  - entrypoint types,
  - sensitive sinks,
  - signed/proof-bearing artifacts,
  - resource-accounting surfaces,
  - lifecycle/state-machine coordinates,
  - fork/version/feature gates,
  - storage/proof/persistence surfaces,
  - p2p and sync pipelines,
  - VM, precompile, native adapter, or cross-runtime boundaries.
- Always include focused queries, when the target has analogous surfaces, for:
  - deterministic finalization or block validation with external, RPC, local-node, snapshot, or background-builder errors;
  - Engine API, payload sidecar, fork-method, optional-field, or method-version mismatches;
  - vote-extension commit info, late or post-quorum data, duplicate votes, aggregate signature validation order, signature canonicalization, and quorum-context binding;
  - trusted-object upstream guarantee failures, including data accepted from consensus/client/provider layers after the normal verifier may no longer run;
  - proposal bodies that accept missing, partial, empty, or many syntactically valid objects;
  - delayed cross-runtime events, source log ordering, adapter/native sink mismatch, same-identifier front-running, and same-block dependent events;
  - asynchronous bridge balance mirrors, stale reserves, delayed withdrawals, cross-direction accounting races, and snapshot overwrite/delta mismatch;
  - signature or proof malleability where bytewise uniqueness is used after semantic verification;
  - raw-byte duplicate or conflict checks after signature/proof validity, including finalization or persistence paths that compare signature bytes rather than signer/message identity;
  - public-key or identity admission where source-side syntax, length, address, or allowlist checks differ from downstream semantic uniqueness, ownership, or curve-validation checks;
  - two-actor delayed-sink front-running where one actor can reserve a native identity, public key, registry key, claim, or validator slot before another actor's source-accepted action reaches the sink;
  - deterministic consensus callbacks that start optional helper work or optimistic background work and return its local errors to the consensus engine;
  - malformed payload, unsupported fork/method field, or dependency validation errors retried as if they were transient transport failures;
  - pending-object retention growth where valid but useless roots, receipts, votes, claims, jobs, or attestations are scanned every block.
  - proposal cardinality/resource issues involving missing required system work, many empty objects, no-op messages, syntactically valid low-work transactions, or expensive decode/storage with little execution.
  - detached-data or blob-like transaction families where builders preserve side data but validators or importers pass empty/default side arguments to a fork-versioned execution API.
  - post-quorum metadata poisoning where late or weakly verified commit/certificate entries are retained and repeatedly included by proposers.
  - public-key syntax-vs-curve mismatches where a length-valid key is stored and a later validator-set, signer, decompression, or quorum consumer fails.
  - two-actor identity reservations where one actor locks a sink-side public key, registry key, validator slot, withdrawal identifier, or claim identifier before another actor's source-side value or authority reaches the sink.
  - retained fake-root or fake-claim sets where cheap inserts accumulate until approval, trimming, export, or every-block scans become expensive.
  - accepted empty transaction lists or many empty transaction entries that are valid enough for proposal acceptance but consume decode, storage, replay, or hash work.
- Run the corpus search tool with `repo-context.md` as a query file and with focused family filters when useful.

Example commands:

```bash
/testing/dlt-auditor/bin/search-corpus \
  --query-file /path/to/run/repo-context.md \
  --top-k 30 \
  --output /path/to/run/corpus-retrieval/all-families.md

/testing/dlt-auditor/bin/search-corpus \
  --query-file /path/to/run/repo-context.md \
  --family resource_accounting_and_limits \
  --top-k 12 \
  --output /path/to/run/corpus-retrieval/resource-accounting.md
```

Step 2: Read compact corpus artifacts only.
- Prefer the normalized record plus root-cause, code-shape, and validation cards.
- Do not pull full raw finding markdown by default.
- Skip low-quality entries that have no search motifs, no violated invariant, or no false-positive cautions.

Step 3: Convert matches into target-code searches.
For each promising match:
1. Extract the generic missing property.
2. Extract code-shape motifs and suspicious asymmetries.
3. Translate those motifs into `rg` searches and file/function inspections in the target repo.
4. Look for analogous code shapes, not identical names.
5. Record the target files/functions checked.
6. Record whether the match produced:
   - a concrete candidate,
   - a killed hypothesis,
   - or no relevant target surface.

Step 4: Produce `corpus-match-index.md`.
For each corpus match used, include:
- corpus entry id,
- corpus family and missing property,
- target surface searched,
- search commands or code paths inspected,
- result: candidate / killed / no target analogue,
- candidate id if one was created,
- false-positive cautions applied.

Step 5: Produce `corpus-pattern-candidates.md`.
For each surviving pattern-derived candidate, include:
- title,
- target file/function,
- corpus pattern that inspired it,
- intended invariant,
- suspected missing property,
- attacker preconditions,
- possible impact,
- what evidence would confirm it,
- what evidence would kill it.

Constraints:
- Corpus similarity is never evidence by itself.
- Do not copy historical repo-specific paths, function names, or constants into the target claim.
- Prefer killing weak pattern matches over generating inflated candidates.
- Every surviving candidate must still pass `02_validation_and_impact.md`.
```
