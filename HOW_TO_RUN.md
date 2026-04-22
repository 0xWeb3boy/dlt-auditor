# How To Run

This is the short operator guide for using the audit system with one agent or multiple agents.

## Single-Agent Workflow

1. Create a run folder under [runs](/testing/dlt-ai-audit-system/runs).
   Example: `dlt-ai-audit-system/runs/2026-04-22-example-chain/`

2. Copy [repo-context-template.md](/testing/dlt-ai-audit-system/templates/repo-context-template.md) to `repo-context.md`.

3. Run [00_protocol_mapper.md](/testing/dlt-ai-audit-system/00_protocol_mapper.md) and have the agent fill `repo-context.md`.

4. Pick one prompt family from [prompts](/testing/dlt-ai-audit-system/prompts).

5. Copy [family-scan-template.md](/testing/dlt-ai-audit-system/templates/family-scan-template.md) to `family-scan-<family>.md`.

6. Run [01_base_hunter.md](/testing/dlt-ai-audit-system/01_base_hunter.md) together with the chosen family prompt and have the agent fill that family scan.

7. For the strongest candidate, copy [candidate-template.md](/testing/dlt-ai-audit-system/templates/candidate-template.md) to `candidate-<id>.md`.

8. Run [02_validation_and_impact.md](/testing/dlt-ai-audit-system/02_validation_and_impact.md) and have the agent fill the candidate file.

9. Repeat for other families.

## Corpus Ingestion Workflow

If you already have `validated-findings/kept` from another repo and want to turn them into corpus artifacts, use:

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/repo
```

That command now prepares the bundle for a parallel `03_enrich` pass by default, using six workers unless you override it.

If you want a different worker count, use:

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/repo --parallel-workers 8
```

That command prepares a timestamped import bundle under `corpus/imports/` with:

- raw finding copies
- normalized record stubs
- retrieval card stubs
- eval stubs
- an import manifest

Unless you set `--parallel-workers 1`, it also prepares `parallel-enrichment/` inside the bundle with:

- `worker-XX.md` prompts
- `worker-XX-assignment.json` file-ownership manifests
- `worker-XX-findings.txt` finding lists
- a `parallel-enrichment/manifest.json` worker index

After that, use [03_enrich_corpus_import.md](/testing/dlt-ai-audit-system/03_enrich_corpus_import.md) to turn the stubs into higher-quality corpus artifacts.

## Prompt Refinement Workflow

If the source repo already has `validated-findings/kept` and you want to improve the reusable prompt pack rather than just ingest the corpus, use [04_refine_prompt_pack_from_findings.md](/testing/dlt-ai-audit-system/04_refine_prompt_pack_from_findings.md).

That workflow asks the agent to:

- analyze the confirmed findings in repo context,
- extract reusable hunt recipes,
- cluster them by failure mechanism,
- compare those clusters to the current prompt pack,
- refine existing prompts where possible,
- and add a new family prompt only when the mechanism is distinct enough to justify it.

## Multi-Agent Workflow

1. A lead agent fills `repo-context.md`.

2. Every worker agent reads the same `repo-context.md`.

3. Each worker takes one prompt family and fills one `family-scan-<family>.md`.

4. The lead agent compares the family scans and picks the strongest candidates.

5. A lead or validator agent fills one `candidate-<id>.md` per serious issue.

For corpus enrichment, you can use the same pattern after import: use the default six-worker plan or prepare the bundle with `--parallel-workers N`, then start one worker per `parallel-enrichment/worker-XX.md` and have each worker edit only the files listed in its `worker-XX-assignment.json`.

## Suggested Family Order

If you want a practical default order, use:

1. `10_authz_and_role_gates.md`
2. `11_signature_binding_and_signer_scope.md`
3. `14_resource_accounting_and_limits.md`
4. `15_state_machine_and_lifecycle_consistency.md`
5. `16_staking_registry_and_accountability.md`
6. `12_attestation_trust_and_freshness.md`
7. `13_input_validation_and_invariant_enforcement.md`
8. `17_checked_arithmetic_and_parameter_bounds.md`

## File Discipline

Keep the intermediate files:

- short,
- structured,
- factual,
- and explicit about uncertainty.

Do not turn them into giant scratchpads or raw command dumps.
