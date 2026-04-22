# Findings Corpus

This folder is the structured knowledge layer for the audit system.

Use it to convert human-written findings into machine-usable records for:

- retrieval,
- taxonomy refinement,
- and evaluation.

The operational prompts should stay generic. This corpus is where historical knowledge lives.

## What To Store Here

Each finding should ideally exist in four forms:

1. `record`
   The canonical normalized representation of the finding.

2. `root-cause-card`
   A short retrieval artifact focused on the violated invariant and the missing property.

3. `code-shape-card`
   A short retrieval artifact focused on code patterns, asymmetries, and search motifs.

4. `validation-card`
   A short retrieval artifact focused on what confirmed the issue and what could have invalidated it.

## Recommended Layout

```text
corpus/
  README.md
  SCHEMA.md
  CONVERSION_GUIDE.md
  templates/
    finding-record-template.yaml
    root-cause-card-template.md
    code-shape-card-template.md
    validation-card-template.md
    eval-record-template.yaml
  records/
  cards/
    root-cause/
    code-shape/
    validation/
  evals/
```

## Suggested Workflow

1. Read one finding markdown file from `validated-findings/kept`.
2. Convert it into one normalized YAML record in `records/`.
3. Create the three short retrieval cards in `cards/`.
4. Create one eval record in `evals/`.
5. Tag the record by bug family, confidence tier, subsystem, trust boundary, and impact type.

## Fast Path

If you already have a repo with `validated-findings/kept`, you can scaffold the corpus artifacts with:

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/repo
```

That creates a timestamped import bundle under `corpus/imports/`.
By default, it also includes a six-worker `parallel-enrichment/` folder with per-worker prompts and assignment files for multi-agent enrichment. Use `--parallel-workers N` to change that count, or `--parallel-workers 1` to skip the planner.

## Confidence Tiers

Use one of these:

- `tier_a_confirmed`
  Strongest examples. Best for prompt calibration, retrieval exemplars, and evals.

- `tier_b_likely`
  Useful pattern examples. Good for retrieval and taxonomy refinement, but weaker as gold-standard severity anchors.

- `tier_c_provenance_only`
  Useful for background context or taxonomy notes, but too weak or ambiguous to act as a strong runtime exemplar.

## Important Rule

Do not retrieve full raw finding markdown into the agent by default.

Prefer retrieving:

- the normalized record summary,
- plus one or two short cards relevant to the current family and architecture.
