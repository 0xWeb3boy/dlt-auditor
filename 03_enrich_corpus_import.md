# Prompt: Enrich Corpus Import

Use this after running:

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/repo
```

By default, imports now include a six-worker `parallel-enrichment/` plan. Each worker should use its own `parallel-enrichment/worker-XX.md` prompt and only edit the files listed in its matching `worker-XX-assignment.json`. If the importer was run with `--parallel-workers 1`, use this prompt as a single-agent enrichment pass instead.

## Objective

Take an auto-generated corpus import bundle and upgrade its record stubs, retrieval cards, and eval stubs into useful structured knowledge.

## Prompt

```text
You are enriching a prepared corpus import bundle for a blockchain/DLT audit system.

Your job is not to audit the target repo directly. Your job is to turn validated findings into high-quality corpus artifacts.

Inputs:
- The import bundle created by `prepare-corpus-from-repo`
- If present, the worker-specific prompt in `parallel-enrichment/worker-XX.md`
- If present, the worker-specific file-ownership manifest in `parallel-enrichment/worker-XX-assignment.json`
- The original raw finding markdown files, usually in `raw-findings/` or otherwise via the source paths listed in the assignment/source metadata
- The generated stubs in:
  - `records/`
  - `cards/root-cause/`
  - `cards/code-shape/`
  - `cards/validation/`
  - `evals/`

If you are running as one worker in a multi-agent enrichment pass, only edit the findings and files assigned to you.

Your tasks for each finding:
1. Rewrite the violated invariant in plain, generic terms.
2. Identify the missing property more precisely if the stub is too broad.
3. Name the trust boundary crossed.
4. Classify the entrypoint type.
5. Name the sensitive sink.
6. Fill attacker capabilities and exploit preconditions.
7. Fill impact types and a severity guess with a short rationale.
8. Rewrite the code-shape summary so it is concise and reusable.
9. Add search motifs that would help find similar bugs in other repos.
10. Add negative signals and false-positive cautions.
11. Summarize the structural patch pattern.
12. Fill the eval record with the expected family, property, impact band, severity band, and false-positive cautions.

Quality bar:
- Keep the language generic enough to transfer across other blockchains/DLT systems.
- Keep the summary specific enough to still be useful for retrieval.
- Do not copy long passages from the raw finding.
- Distinguish proven issues from likely/hardening cases.
- Prefer reusable invariant language over repo-specific jargon when possible.

Output expectations:
- Updated YAML record
- Updated root-cause card
- Updated code-shape card
- Updated validation card
- Updated eval record
```
