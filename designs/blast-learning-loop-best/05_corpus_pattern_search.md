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
- The shared corpus under `/testing/dlt-ai-audit-system/corpus/imports`.
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
- Run the corpus search tool with `repo-context.md` as a query file and with focused family filters when useful.

Example commands:

```bash
/testing/dlt-ai-audit-system/designs/corpus-search/bin/search-corpus \
  --query-file /path/to/run/repo-context.md \
  --top-k 30 \
  --output /path/to/run/corpus-retrieval/all-families.md

/testing/dlt-ai-audit-system/designs/corpus-search/bin/search-corpus \
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
