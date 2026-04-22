# Blockchain/DLT AI Audit System

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

## Intermediate Artifacts

For better audit quality, especially on large repos or multi-agent runs, keep a small set of structured intermediate files:

- `repo-context.md`
  Purpose: shared understanding of architecture, trust boundaries, state machines, and high-risk modules.

- `family-scan-<family>.md`
  Purpose: one file per bug family with candidate code paths, suspicious asymmetries, and ranked hypotheses.

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
      family-scan-authz.md
      family-scan-signatures.md
      family-scan-state-machine.md
      candidate-01.md
      candidate-02.md
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

By default, that now prepares a six-worker `parallel-enrichment/` plan inside the bundle so `03_enrich` can be split across multiple agents immediately.

If you want a different worker count, use:

```bash
/testing/dlt-ai-audit-system/bin/prepare-corpus-from-repo /path/to/repo --parallel-workers 8
```

That will create a timestamped import bundle under `corpus/imports/` with raw copies, record stubs, retrieval-card stubs, eval stubs, and an import summary. Unless you set `--parallel-workers 1`, it also creates a `parallel-enrichment/` plan inside the bundle with `worker-XX.md` prompts, `worker-XX-assignment.json` ownership files, `worker-XX-findings.txt` lists, and a manifest for multi-agent `03_enrich` runs.
