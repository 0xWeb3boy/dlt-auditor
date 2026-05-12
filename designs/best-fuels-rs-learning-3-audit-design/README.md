# Blockchain/DLT AI Audit System - Corpus Search Design

This design is the corpus-search variant of the audit system.

It keeps the existing max-audit workflow, then adds a corpus pattern search phase between repository mapping and family scans. The goal is to retrieve similar historical vulnerability patterns, translate their search motifs into target-repo searches, and ask the AI auditor to inspect those matches as hypotheses.

Corpus similarity is not evidence by itself. Every pattern-derived candidate still needs target-code reachability, attacker control, a missing property, compensating-control analysis, and impact validation.

## What Is Different From `designs/current`

Additional pieces in this design:

- `05_corpus_pattern_search.md`, a prompt for using corpus records and retrieval cards during an audit.
- `bin/search-corpus`, a lightweight lexical corpus search tool.
- `bin/run-parallel-codex`, a Codex CLI runner that executes shared phases serially and family scans/candidate validations concurrently.
- generated run files:
  - `corpus-match-index.md`
  - `corpus-pattern-candidates.md`
  - `corpus-retrieval/`
  - `agent-prompts/05-corpus-pattern-search.md`
  - `agent-prompts/00-RUN-PARALLEL-CODEX.md`

The shared corpus remains at `/testing/dlt-ai-audit-system/corpus/imports`.

## Run

```bash
/testing/dlt-ai-audit-system/bin/dlt-ai-audit-corpus-search /path/to/blockchain-repo
```

Or directly:

```bash
/testing/dlt-ai-audit-system/designs/corpus-search/bin/dlt-ai-audit-system /path/to/blockchain-repo
```

To search the corpus manually:

```bash
/testing/dlt-ai-audit-system/designs/corpus-search/bin/search-corpus \
  --query-file /path/to/run/repo-context.md \
  --family resource_accounting_and_limits \
  --top-k 12
```

To run a generated audit with multiple Codex workers:

```bash
/testing/dlt-ai-audit-system/bin/run-corpus-search-parallel \
  /testing/dlt-ai-audit-system/designs/corpus-search/runs/<run-name> \
  --jobs 4
```

The runner defaults to `gpt-5.5`, Codex service tier `fast`, reasoning `high` for mapper/corpus/scans, and reasoning `xhigh` for canonicalize/validations/aggregate/final. You can override the split:

```bash
/testing/dlt-ai-audit-system/bin/run-corpus-search-parallel \
  /testing/dlt-ai-audit-system/designs/corpus-search/runs/<run-name> \
  --jobs 4 \
  --service-tier fast \
  --reasoning-effort high \
  --deep-reasoning-effort xhigh \
  --deep-phases canonicalize,validations,aggregate,final
```

The runner uses this order:

1. mapper serially,
2. corpus pattern search serially,
3. family scans in parallel,
4. candidate validations in parallel if `candidate-*.md` files exist,
5. final coverage serially.

Each family worker is instructed to edit only its own `family-scan-*.md` file.

## Original Current-Design Documentation

This folder turns the confirmed patterns in `validated-findings/kept` into a reusable workflow for an AI agent that can be applied to any blockchain or DLT repository.

The findings corpus in this repo came from Oasis, but the workflow below is intentionally generalized. The agent should treat the Oasis findings as examples of recurring bug families, not as assumptions about the target codebase.

## What This System Does

The system helps an agent:

1. onboard onto an unfamiliar blockchain or DLT repository,
2. identify its trust boundaries, critical state machines, and privileged entrypoints,
3. hunt for recurring vulnerability classes,
4. validate whether a candidate issue is real, and
5. assign impact and severity in a disciplined way.

## Generic Threat Model

Before hunting for bugs, the agent should discover the repo-specific equivalents of these common blockchain or DLT surfaces:

1. Transaction admission, mempool, execution, settlement, and finalization.
2. Consensus or ordering logic, including validator, proposer, sequencer, committee, or relayer roles.
3. State commitment, proof verification, checkpointing, historical queries, and storage synchronization.
4. Peer-to-peer networking, node authorization, and cross-node message handling.
5. RPC, admin, operator, relayer, bridge, keeper, or control-plane APIs.
6. Key management, validator identity, signing, attestation, multisig, or proof-verifier flows.
7. Governance-controlled parameters, staking, slashing, elections, accountability, and economic constraints.
8. Lifecycle transitions such as epochs, rounds, sessions, view changes, handoffs, upgrades, checkpoints, or reconfiguration.

Different systems implement these differently, but most serious bugs fit somewhere in those buckets.

## Recommended Sequence

### One-Command Max Setup

For the deepest repeatable workflow, scaffold every audit artifact and an autonomous max-audit driver prompt:

```bash
dlt-ai-audit-system/bin/dlt-ai-audit-system /path/to/blockchain-repo
```

From a workspace that contains this tool, this is usually:

```bash
dlt-ai-audit-system/bin/dlt-ai-audit-system .
```

For a diff-aware audit, pass the previous and current refs when you know them:

```bash
dlt-ai-audit-system/bin/dlt-ai-audit-system . --previous-ref <old-ref> --current-ref HEAD
```

The command creates `runs/<timestamp>-<target>-max-audit/` with:

- `agent-prompts/00-RUN-AUTONOMOUS-MAX-AUDIT.md`, the one-shot prompt to give an AI auditor so it runs the full pipeline automatically,
- a repo-context file,
- `feature-coverage.md` for per-feature coverage accounting,
- `verification-log.md` for build/test entry points, attempts, and blockers,
- one family scan file for every prompt family,
- validation and final-coverage prompts for manual fallback,
- `candidate-index.md`,
- `rejected-candidates.md`,
- `FINAL_AUDIT_REPORT.md`,
- and `MAX_AUDIT_CHECKLIST.md`.

Start with `agent-prompts/00-RUN-AUTONOMOUS-MAX-AUDIT.md` when you want one AI agent to map the repo, establish the diff baseline, fill feature coverage, run every family scan, validate candidates, deduplicate results, log rejected ideas, record build/test attempts or blockers, perform a final coverage pass, and produce the final report. The command does not treat old run reports as live input; keep those under `previous-runs/` and use them only as examples when you intentionally want calibration. A PoC is not required by the generated workflow.

### Manual Sequence

1. Create a run folder, for example `runs/<date>-<target>/`.
   Purpose: keep all intermediate artifacts for one audit together.

2. Run `00_protocol_mapper.md`.
   Purpose: discover the repo's actual architecture, trust boundaries, and terminology.
   Output target: `runs/<run>/repo-context.md`

3. Pick one family prompt from `prompts/`.
   The operational prompts are intentionally generic and do not depend on historical findings.
   Output target: `runs/<run>/family-scan-<family>.md`

4. Run `01_base_hunter.md` together with the chosen family prompt.
   Purpose: enumerate candidate code paths, missing checks, and suspicious asymmetries.

5. For each serious candidate, run `02_validation_and_impact.md`.
   Purpose: turn a suspicion into a defensible finding with impact, severity, exploit preconditions, and counterarguments.
   Output target: `runs/<run>/candidate-<id>.md`

6. If the candidate survives validation, write the final report using the output schema in `02_validation_and_impact.md`.

## Prompt Pack

The prompt files are organized by recurring issue family instead of one file per historical finding.

- `prompts/10_authz_and_role_gates.md`
- `prompts/11_signature_binding_and_signer_scope.md`
- `prompts/12_attestation_trust_and_freshness.md`
- `prompts/13_input_validation_and_invariant_enforcement.md`
- `prompts/14_resource_accounting_and_limits.md`
- `prompts/15_state_machine_and_lifecycle_consistency.md`
- `prompts/16_staking_registry_and_accountability.md`
- `prompts/17_checked_arithmetic_and_parameter_bounds.md`
- `prompts/18_authoritative_state_and_boundary_enforcement.md`
- `prompts/19_consensus_fork_and_payload_rule_validation.md`
- `prompts/20_authenticated_state_proof_and_persistence_integrity.md`
- `prompts/21_peer_sync_progress_and_response_binding.md`
- `prompts/22_ledger_accounting_and_invariant_coverage.md`
- `prompts/23_zk_circuit_witness_and_public_data_binding.md`

## Intermediate Artifacts

For better audit quality, especially on large repos or multi-agent runs, keep a small set of structured intermediate files:

- `repo-context.md`
  Purpose: shared understanding of architecture, trust boundaries, state machines, and high-risk modules.

- `family-scan-<family>.md`
  Purpose: one file per bug family with candidate code paths, suspicious asymmetries, and ranked hypotheses.

- `feature-coverage.md`
  Purpose: per-feature coverage accounting across changed files, reviewed functions, tests searched, candidates, rejected ideas, and residual risk.

- `verification-log.md`
  Purpose: build/test entry points, commands attempted, test references reviewed, and blockers.

- `candidate-<id>.md`
  Purpose: one deep validation dossier per candidate issue.

Templates for those files live in [templates](/testing/dlt-ai-audit-system/templates).

## Recommended Run Layout

Use a per-audit folder layout like this:

```text
dlt-ai-audit-system/
  runs/
    2026-04-22-target-name/
      repo-context.md
      feature-coverage.md
      verification-log.md
      family-scan-authz.md
      family-scan-signatures.md
      family-scan-state-machine.md
      candidate-index.md
      rejected-candidates.md
      candidate-01.md
      candidate-02.md
      final-coverage-report.md
      FINAL_AUDIT_REPORT.md
```

You do not need every file for every run. The important thing is that all agents in the same audit read from the same `repo-context.md` and write short, structured outputs.

## Severity Heuristics

Use these as defaults unless the code supports a stronger or weaker conclusion:

- `Critical`: direct consensus break, forged finalized state acceptance, bridge or settlement compromise, unauthorized mint or burn, or broad privileged secret compromise.
- `High`: missing authentication on privileged interfaces, unauthorized validator or committee actions, slashability bypass, signer-scope failure in consensus-sensitive code, or privileged data or key disclosure.
- `Medium`: denial of service, fee or quota bypass, stale trust or policy state, malformed-input panic, premature readiness or registration, incorrect voting-power or liveness accounting, or proof/query verification gaps.
- `Low`: debug-only hardening, local misconfiguration prevention, or correctness fixes without a credible attacker-controlled trigger.
- `Informational`: no practical security consequence.

## Generic Review Rules

When evaluating a candidate, the agent should ask:

1. Does the bug cross a trust boundary between users, validators, full nodes, sequencers, relayers, bridge operators, committees, governance actors, or enclaves/coprocessors?
2. Does the code verify cryptographic validity but forget authorization, role membership, scope binding, nonce binding, chain binding, or freshness?
3. Does the state machine use multiple related coordinates like height, round, epoch, session, view, checkpoint, handoff, channel, or request ID that can drift out of sync?
4. Is there any path that performs meaningful work before gas charging, fee charging, quota checks, queue admission, or simulation-aware accounting?
5. Is a field, capability, message type, or policy accepted before the protocol version, feature flag, fork activation, or governance state that is supposed to enable it?

## Provenance

If you want to preserve where the prompt taxonomy came from without polluting the runtime prompts, see [prompt-provenance.md](/testing/dlt-ai-audit-system/prompt-provenance.md).

## Corpus Ingestion

If you already have `validated-findings/kept` in another repo, you can prepare the next-stage corpus artifacts with one command:

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/repo
```

That will create a timestamped import bundle under `corpus/imports/` with raw copies, record stubs, retrieval-card stubs, eval stubs, and an import summary.

### How To Run `03_enrich`

You will often start from the source repo that contains `validated-findings/kept`, not from a bundle path you already know.

Use an instruction like:

```text
Run the dlt-ai-audit-system corpus pipeline on /path/to/target-repo.

Prepare the import bundle from validated-findings/kept and then enrich the generated records, cards, and evals.

Use /testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/target-repo to create the bundle under /testing/dlt-ai-audit-system/corpus/imports/.
Then use /testing/dlt-ai-audit-system/03_enrich_corpus_import.md on the newly created import bundle.

Read the bundle's SUMMARY.md, raw-findings/, records/, cards/, and evals/ folders.
Enrich the generated records, cards, and evals in place.
```

In practice, this produces a timestamped import bundle under `corpus/imports/`, for example:

```text
/testing/dlt-ai-audit-system/corpus/imports/20260422-162106Z-base
```

## Prompt Pack Refinement

If you want to improve the reusable runtime prompts using a repo that already has confirmed findings under `validated-findings/kept`, use [04_refine_prompt_pack_from_findings.md](/testing/dlt-ai-audit-system/04_refine_prompt_pack_from_findings.md).

That workflow is intentionally stricter than "one prompt per finding". Its goal is to derive family-level hunt logic from real findings, compare that against the current prompt pack, refine existing prompts where possible, and add new prompt families only when the mechanism is genuinely distinct and portable.

### How To Run `04_refine`

Use an instruction like:

```text
Use /testing/dlt-ai-audit-system/04_refine_prompt_pack_from_findings.md.

The target repo is /path/to/target-repo.
Analyze its validated-findings/kept folder in repo context.
Then compare what you learn against /testing/dlt-ai-audit-system and propose concrete prompt-pack improvements.
```
