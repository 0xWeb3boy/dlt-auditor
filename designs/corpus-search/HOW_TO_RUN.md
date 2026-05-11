# How To Run

This is the short operator guide for using the audit system.

## Single-Agent Workflow

### Max Audit Command

To set up the full workflow and the autonomous driver prompt for a target repo, run:

```bash
dlt-ai-audit-system/bin/dlt-ai-audit-system /path/to/blockchain-repo
```

From this Sherlock workspace, for example:

```bash
dlt-ai-audit-system/bin/dlt-ai-audit-system .
```

When there is an intended upgrade or contest diff, provide refs:

```bash
dlt-ai-audit-system/bin/dlt-ai-audit-system . --previous-ref <old-ref> --current-ref HEAD
```

The command creates a timestamped folder under `dlt-ai-audit-system/runs/` with:

- `agent-prompts/00-RUN-AUTONOMOUS-MAX-AUDIT.md`
- `repo-context.md`
- `feature-coverage.md`
- `verification-log.md`
- one `family-scan-*.md` file for every prompt family
- `candidate-index.md`
- `rejected-candidates.md`
- `FINAL_AUDIT_REPORT.md`
- manual fallback prompts under `agent-prompts/`
- `MAX_AUDIT_CHECKLIST.md`

For a one-pass AI audit, give your agent `agent-prompts/00-RUN-AUTONOMOUS-MAX-AUDIT.md`. That prompt instructs the agent to map the repository, establish the diff baseline, fill feature coverage, run every family scan, validate plausible Medium-or-higher candidates, deduplicate findings, log rejected ideas, record build/test attempts or blockers, run final coverage, and fill the final report. A PoC is not required by the generated workflow.

For manual operation, start with `agent-prompts/00-protocol-mapper.md`, then run every family prompt, validate candidates, and finish with `agent-prompts/99-final-coverage-pass.md`.

Old example reports should live in `previous-runs/` and should not be mixed into a fresh run unless you intentionally want calibration examples.

### Manual Workflow

1. Create a run folder under [runs](/testing/dlt-ai-audit-system/runs).
   Example: `dlt-ai-audit-system/runs/2026-04-22-example-chain/`

2. Copy [repo-context-template.md](/testing/dlt-ai-audit-system/templates/repo-context-template.md) to `repo-context.md`.

3. Run [00_protocol_mapper.md](/testing/dlt-ai-audit-system/00_protocol_mapper.md) and have the agent fill `repo-context.md`, `feature-coverage.md`, and `verification-log.md`.

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

That command prepares a timestamped import bundle under `corpus/imports/` with:

- raw finding copies
- normalized record stubs
- retrieval card stubs
- eval stubs
- an import manifest

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

## Suggested Family Order

If you want a practical default order, use:

1. `10_authz_and_role_gates.md`
2. `11_signature_binding_and_signer_scope.md`
3. `14_resource_accounting_and_limits.md`
4. `15_state_machine_and_lifecycle_consistency.md`
5. `19_consensus_fork_and_payload_rule_validation.md`
6. `20_authenticated_state_proof_and_persistence_integrity.md`
7. `16_staking_registry_and_accountability.md`
8. `12_attestation_trust_and_freshness.md`
9. `13_input_validation_and_invariant_enforcement.md`
10. `18_authoritative_state_and_boundary_enforcement.md`
11. `17_checked_arithmetic_and_parameter_bounds.md`
12. `23_zk_circuit_witness_and_public_data_binding.md`

## File Discipline

Keep the intermediate files:

- short,
- structured,
- factual,
- and explicit about uncertainty.

Do not turn them into giant scratchpads or raw command dumps.
