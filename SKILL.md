---
name: dlt-auditor
description: Run DLT Auditor stable audit designs and blind audit suites against target codebases from this repository. Use when the user asks to run, scaffold, resume, configure, or explain dlt-auditor audit execution, including max, optimal, or custom prompt-pack tiers, Codex and Claude Code agent modes, blind-suite integrity rules, worker-limit recovery, design selection, or the runtime-focused dlt-auditor workflow.
---

# DLT Auditor

Use this repository as the runtime for stable audit designs from `designs/` against target codebases. Run commands from this skill/repository root.

Do not add or reintroduce learning-loop features, benchmark ground truth, candidate scoring, scorecards, miss analysis, leaderboards, promotion workflows, or refinement systems unless the user explicitly asks to rebuild that separate system.

## Blind Integrity

During blind audit execution, keep audit workers separated from answer-key material.

Do not read known findings, benchmark ground truth, scorecards, miss analyses, result records, leaderboards, refinement plans, audit-output snapshots, candidate result archives, prior round folders, sibling suite outputs, or stable `designs/*/runs/**` output.

Preserve generated suites when worker limits or external interruptions occur. Resume instead of recreating unless the user explicitly asks to replace the suite.

## Agent Choice

Use Codex by default:

```text
--agent codex --service-tier standard --reasoning-effort high --deep-reasoning-effort xhigh --deep-phases canonicalize,validations,aggregate,final
```

Use Claude Code when the user asks for Claude, Claude Code, or `--agent claude`:

```text
--agent claude
```

For Claude Code, do not pass Codex reasoning or service-tier overrides. Use `--claude-path` or `--claude-add-dir` only when the user supplies those needs or local execution requires them.

## Tiers

Treat "prompt packs" and "design packs" as the stable design folders under `designs/`.

Support these tier invocations:

```text
$dlt-auditor max ...
$dlt-auditor optimal ...
$dlt-auditor custom ...
```

If the target repository or suite name is missing, infer a reasonable suite name from the target basename, tier, and timestamp when possible. Ask only when the target repository path is missing or ambiguous.

### Max

Use every runnable design pack under `designs/`.

Discover packs with:

```bash
bin/run-blind-suite --list-designs
```

or, if needed:

```bash
find designs -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort
```

Then run one blind suite with every discovered pack by repeating `--design <design-name>`.

### Optimal

Analyze the target project and available design packs, choose only the packs that best fit the project, and run them. Select at most 5 packs.

Use this selection process:

1. Inspect target repo metadata such as `README*`, package manifests, lockfiles, language/framework files, top-level directories, and dependency names.
2. Inspect design pack names and high-level pack files such as `designs/<name>/00_protocol_mapper.md`, `01_base_hunter.md`, `02_validation_and_impact.md`, and `05_corpus_pattern_search.md`.
3. Do not inspect generated runs or answer-key material while selecting.
4. Prefer packs whose protocol, ecosystem, implementation language, or audit venue matches the target.
5. If fewer than 5 packs clearly fit, run only the clear fits. If none clearly fit, choose the closest generally applicable packs and state that the selection is a best-effort match.

After choosing, immediately run one blind suite with the selected packs by repeating `--design <design-name>`.

### Custom

Use exactly the design packs named by the user. Validate that each named pack exists under `designs/`; if a name is misspelled, list the available packs and ask for correction.

## One Design

Scaffold a single design run:

```bash
bin/run-design <design-name> /path/to/target-repo --run-name <run-name> --parallel-jobs 8
```

Then execute the generated design run with that design's runner.

Codex:

```bash
designs/<design-name>/bin/run-parallel-codex designs/<design-name>/runs/<run-name> --jobs 8 --agent codex --service-tier standard --reasoning-effort high --deep-reasoning-effort xhigh --deep-phases canonicalize,validations,aggregate,final
```

Claude Code:

```bash
designs/<design-name>/bin/run-parallel-codex designs/<design-name>/runs/<run-name> --jobs 8 --agent claude
```

If worker limits are exhausted, preserve the run and resume with `--resume` if supported by the runner.

## Blind Suites

Prefer blind suites when running one or more designs as a benchmark-style audit. Outputs live under `runs/<suite-name>/`.

List available designs when the user has not specified one:

```bash
bin/run-blind-suite --list-designs
```

Start a Codex blind suite:

```bash
bin/run-blind-suite --repo /path/to/target-repo --suite-name <suite-name> --design <design-name> --parallel-jobs 8 --agent codex --service-tier standard --reasoning-effort high --deep-reasoning-effort xhigh --deep-phases canonicalize,validations,aggregate,final
```

Start a Claude Code blind suite:

```bash
bin/run-blind-suite --repo /path/to/target-repo --suite-name <suite-name> --design <design-name> --parallel-jobs 8 --agent claude
```

Repeat `--design <design-name>` for multiple designs if requested.

Resume an interrupted or worker-limited suite:

```bash
bin/run-blind-suite --suite-name <suite-name> --resume
```

Use `--scaffold-only` when the user asks to prepare isolated runs without launching workers. Use `--force` only when the user explicitly wants to replace an existing suite or run.
