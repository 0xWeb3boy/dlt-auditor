# Do That From That Repo

This is the shortest workflow for turning `validated-findings/kept` into corpus artifacts.

## Command

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/repo
```

Example:

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /testing/oasis-core
```

## What It Does

Given a repo path, the command:

1. finds `validated-findings/kept`
2. creates a timestamped import bundle under `corpus/imports/`
3. copies the raw finding markdown files into that bundle
4. creates one normalized record stub per finding
5. creates one root-cause card per finding
6. creates one code-shape card per finding
7. creates one validation card per finding
8. creates one eval record per finding
9. writes a `manifest.json` and `SUMMARY.md`

## What It Does Not Do

It does not fully understand the finding by itself.

The generated files are intentionally prepared as structured stubs. They still need enrichment by an AI agent or a human reviewer.

## Typical Next Step

After running the command, use the generated import bundle as the working folder for enrichment.

In practice, that means:

1. open the new `SUMMARY.md`
2. review the generated `records/`
3. enrich the cards and evals
4. then merge the good records into your long-lived corpus
