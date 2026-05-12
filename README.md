# DLT AI Audit System

This repository now contains two runnable audit-system designs side by side.

## Layout

- `designs/current/`
  The existing max-audit workflow. It maps a repo, runs generic family prompts, validates candidates, and produces a final report.

- `designs/corpus-search/`
  A corpus-search-driven variant. It keeps the current workflow, then adds a corpus pattern search phase that retrieves similar historical vulnerability patterns and turns their motifs into target-code searches.

- `corpus/`
  Shared vulnerability corpus data used by both designs. It stays at the repo root so the two designs do not duplicate imported findings.

## Run The Current Design

```bash
/testing/dlt-ai-audit-system/bin/dlt-ai-audit-current /path/to/blockchain-repo
```

The old command still points to the current design:

```bash
/testing/dlt-ai-audit-system/bin/dlt-ai-audit-system /path/to/blockchain-repo
```

## Run The Corpus-Search Design

```bash
/testing/dlt-ai-audit-system/bin/dlt-ai-audit-corpus-search /path/to/blockchain-repo
```

This creates a run under `designs/corpus-search/runs/` with the normal audit artifacts plus:

- `corpus-match-index.md`
- `corpus-pattern-candidates.md`
- `corpus-retrieval/`
- `agent-prompts/05-corpus-pattern-search.md`

To execute the generated corpus-search run with multiple Codex workers:

```bash
/testing/dlt-ai-audit-system/bin/run-corpus-search-parallel \
  /testing/dlt-ai-audit-system/designs/corpus-search/runs/<run-name> \
  --jobs 8
```

The parallel runner keeps the mapper and corpus-search phases serial, then runs independent family scans concurrently. Use `--jobs 1` to disable parallelism.
By default it uses `gpt-5.5` on Codex service tier `standard`, with reasoning `high` for discovery phases and `xhigh` for canonicalization, validation, aggregation, and final review. Override with `--model`, `--service-tier fast`, `--reasoning-effort`, `--deep-reasoning-effort`, or `--deep-phases` when needed.

## Search The Corpus Directly

```bash
/testing/dlt-ai-audit-system/bin/search-corpus \
  --query "transaction decoder unbounded list resource accounting" \
  --family resource_accounting_and_limits \
  --top-k 10
```

Corpus matches are hypothesis generators only. A real finding still needs target-code reachability, attacker capability, a missing property, and concrete impact.

## Corpus Ingestion

The corpus ingestion command still works from the root wrapper:

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/repo
```

## Design Lab

Use `design-lab/` to evaluate and improve designs against previous competitions while keeping ground truth separate from blind audit runs:

```bash
/testing/dlt-ai-audit-system/bin/design-lab init-benchmark \
  --name contest-name \
  --repo /path/to/competition/repo \
  --findings /path/to/known/findings

/testing/dlt-ai-audit-system/bin/design-lab start-round \
  --benchmark contest-name \
  --design corpus-search \
  --round 1
```

The lab creates scoring and refinement prompts for each round. Promote a reviewed refinement into `designs/` with:

```bash
/testing/dlt-ai-audit-system/bin/design-lab create-candidate \
  --loop-name contest-name-corpus-loop \
  --candidate round-02-a \
  --source-design corpus-search

/testing/dlt-ai-audit-system/bin/design-lab start-round \
  --benchmark contest-name \
  --candidate round-02-a \
  --loop-name contest-name-corpus-loop \
  --round 2

/testing/dlt-ai-audit-system/bin/design-lab promote-best \
  --loop-name contest-name-corpus-loop \
  --new-design eval-trained-contest-name-v1
```

Experimental prompt packs and exact found/partial/missed result records stay under `design-lab/runs/<loop>/`. Only the best scored candidate/source should be copied into `designs/`.

Blind audit runs are not allowed to read benchmark ground truth or previous learning-loop results. Generated audit prompts now explicitly forbid using `design-lab/benchmarks/**`, benchmark `ground-truth/**`, and prior `design-lab/runs/**` scoring/refinement artifacts while producing blind findings.

If Codex limits are exhausted during a learning-loop audit, do not recreate the round. Resume it after limits refill:

```bash
/testing/dlt-ai-audit-system/bin/design-lab resume-audit \
  --round-dir /testing/dlt-ai-audit-system/design-lab/runs/<run>/round-XX \
  --parallel-jobs 8
```

Learning-loop audit execution uses the same default speed/reasoning split: service tier `standard`, `high` for mapper/corpus/scans, and `xhigh` for canonicalize/validations/aggregate/final. Add `--service-tier`, `--reasoning-effort`, `--deep-reasoning-effort`, or `--deep-phases` to `start-round --execute-audit` or `resume-audit` to change it.

To get a ready-to-paste prompt for the whole learning loop:

```bash
/testing/dlt-ai-audit-system/bin/learning-loop-prompt \
  --repo /path/to/competition/repo \
  --findings /path/to/known/findings.md \
  --benchmark contest-name
```

The canonical reusable prompt lives at `design-lab/prompts/run-learning-loop.md`. In a future Codex session, you can say:

```text
run learning loop from dlt-ai-audit-system on this codebase
```

and provide the known findings path.
