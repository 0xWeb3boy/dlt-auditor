# Prompt: Run DLT AI Audit Learning Loop

Use this prompt when the operator asks to run the eval-driven learning loop for `dlt-ai-audit-system` on a previous competition codebase.

## Inputs

- Audit system root: `{{SYSTEM_ROOT}}`
- Competition repo: `{{COMPETITION_REPO}}`
- Known findings file or directory: `{{FINDINGS_PATH}}`
- Benchmark name: `{{BENCHMARK_NAME}}`
- Loop name: `{{LOOP_NAME}}`
- Starting design: `{{STARTING_DESIGN}}`
- Max rounds: `{{MAX_ROUNDS}}`
- Parallel jobs: `{{PARALLEL_JOBS}}`
- Reasoning effort: `{{REASONING_EFFORT}}`
- Deep reasoning effort: `{{DEEP_REASONING_EFFORT}}`
- Deep reasoning phases: `{{DEEP_PHASES}}`
- Final promoted design name: `{{PROMOTED_DESIGN}}`

If the competition repo or findings path is missing, ask for the missing path before starting. If the operator says "this codebase", use the current repository as the competition repo unless the current repository is `dlt-ai-audit-system` itself.

## Guardrails

- The blind audit workers must never read the known findings.
- The known findings are only for post-run scoring, miss analysis, and prompt/design refinement.
- During blind audit execution, do not read `design-lab/benchmarks/**`, benchmark `ground-truth/**`, or previous learning-loop artifacts under `design-lab/runs/**`.
- During blind audit execution, do not read prior `scorecard.md`, `misses.md`, `result-record.json`, `design-refinement-plan.md`, `leaderboard.md`, `audit-output-snapshot/**`, candidate `results/**`, or prior round folders.
- If the active candidate design lives under `design-lab/runs/<loop>/candidates/<candidate>/design/`, the candidate's own design files and its generated audit run directory are allowed. Other loop/scoring/refinement artifacts remain forbidden.
- Do not put exact historical file paths, function names, constants, exploit payloads, or answer trails into runtime prompts.
- Do not edit the audited competition repo to improve results.
- Do not edit benchmark ground truth, scorecards, or result records to make a candidate look better.
- Store every candidate prompt pack, audit output snapshot, scorecard, miss analysis, and structured result under `design-lab/runs/{{LOOP_NAME}}/`.
- Keep `designs/` for stable runnable winners only. Use `promote-best` to copy the best scored source/candidate there.
- Candidate prompt/design edits can be broad: rewrite, delete, add, split, merge, rename, reorder, or reorganize prompts/templates/scripts as long as the change helps the target vulnerability class be found in future unknown repositories and the candidate remains runnable.

## Task

Run the complete learning loop. Stay with it until either all known findings are found with acceptable false positives, the max round is reached, or progress clearly stalls.

Use reasoning `{{REASONING_EFFORT}}` for discovery phases and `{{DEEP_REASONING_EFFORT}}` for `{{DEEP_PHASES}}` unless the operator explicitly overrides that split.

## Step 1: Prepare

Run:

```bash
cd {{SYSTEM_ROOT}}
bin/design-lab --help
```

Confirm the competition repo exists and the known findings path exists. Confirm the known findings are outside the competition repo when possible.

## Step 2: Register Benchmark

Run:

```bash
bin/design-lab init-benchmark \
  --name {{BENCHMARK_NAME}} \
  --repo {{COMPETITION_REPO}} \
  --findings {{FINDINGS_PATH}} \
  --force
```

This copies the known findings into `design-lab/benchmarks/{{BENCHMARK_NAME}}/ground-truth/` for scoring only.

## Step 3: Run Round 1 Blind

Run:

```bash
bin/design-lab start-round \
  --benchmark {{BENCHMARK_NAME}} \
  --design {{STARTING_DESIGN}} \
  --loop-name {{LOOP_NAME}} \
  --round 1 \
  --max-rounds {{MAX_ROUNDS}} \
  --execute-audit \
  --parallel-jobs {{PARALLEL_JOBS}} \
  --reasoning-effort {{REASONING_EFFORT}} \
  --deep-reasoning-effort {{DEEP_REASONING_EFFORT}} \
  --deep-phases {{DEEP_PHASES}} \
  --force
```

The blind audit output will be under the design run directory named in `design-lab/runs/{{LOOP_NAME}}/round-01/round-manifest.json`.

Do not open the benchmark ground truth, previous loop results, scorecards, misses, or refinement plans while the blind audit is running. Those files are only for the scoring/refinement steps after the blind audit completes.

## Step 4: Score Round 1

Open:

```text
design-lab/runs/{{LOOP_NAME}}/round-01/score-blind-run.md
```

Use that scoring prompt to compare the blind audit output against the known findings by root-cause/mechanism equivalence, not keyword overlap.

Fill these files:

```text
design-lab/runs/{{LOOP_NAME}}/round-01/scorecard.md
design-lab/runs/{{LOOP_NAME}}/round-01/misses.md
design-lab/runs/{{LOOP_NAME}}/round-01/result-record.json
```

The structured `result-record.json` must include:

- numeric `score`,
- total known findings,
- exact found ground-truth finding ids/titles,
- exact partial ground-truth finding ids/titles,
- exact missed ground-truth finding ids/titles,
- matching blind-audit candidate ids/files,
- false positives,
- duplicate groups,
- short notes on ambiguous scoring.

Then run:

```bash
bin/design-lab record-result \
  --round-dir design-lab/runs/{{LOOP_NAME}}/round-01 \
  --force
```

## Step 5: Decide Whether To Continue

Stop and promote if all known findings are found with acceptable false positives.

Continue if there are missed or partial findings, meaningful false positives, or coverage gaps worth improving.

## If Codex Limits Are Exhausted

If `start-round --execute-audit` or a runner stops because Codex quota/rate limits are exhausted:

1. Do not rerun `start-round --force` for that same round.
2. Do not delete the round directory or the design run directory.
3. Wait for the limit to refill.
4. Resume the same round with:

```bash
bin/design-lab resume-audit \
  --round-dir design-lab/runs/{{LOOP_NAME}}/round-XX \
  --parallel-jobs {{PARALLEL_JOBS}} \
  --reasoning-effort {{REASONING_EFFORT}} \
  --deep-reasoning-effort {{DEEP_REASONING_EFFORT}} \
  --deep-phases {{DEEP_PHASES}}
```

Replace `round-XX` with the interrupted round, for example `round-03`.

The runner stores completed worker checkpoints under the interrupted audit run's `agent-logs/runner-state/` directory, so resume skips already completed mapper/corpus/family-scan/validation/final prompts.

## Step 6: Refine Generally

Open:

```text
design-lab/runs/{{LOOP_NAME}}/round-01/refine-design-from-misses.md
```

Use that prompt to write:

```text
design-lab/runs/{{LOOP_NAME}}/round-01/design-refinement-plan.md
```

The refinement plan may recommend broad changes, including deleting old prompt logic, adding new families, restructuring templates, changing runner/scaffolding behavior, or replacing vague checklist text with concrete class-level search and validation logic.

The refinement must stay general to the vulnerability class/mechanism. Do not encode historical answer locations.

## Step 7: Create Candidate For Round 2

Run:

```bash
bin/design-lab create-candidate \
  --loop-name {{LOOP_NAME}} \
  --candidate round-02-a \
  --source-design {{STARTING_DESIGN}} \
  --force
```

Apply the approved general improvements from the refinement plan inside:

```text
design-lab/runs/{{LOOP_NAME}}/candidates/round-02-a/design/
```

Do not edit `designs/{{STARTING_DESIGN}}/` directly.

## Step 8: Run And Score Round 2

Run:

```bash
bin/design-lab start-round \
  --benchmark {{BENCHMARK_NAME}} \
  --candidate round-02-a \
  --loop-name {{LOOP_NAME}} \
  --round 2 \
  --max-rounds {{MAX_ROUNDS}} \
  --execute-audit \
  --parallel-jobs {{PARALLEL_JOBS}} \
  --reasoning-effort {{REASONING_EFFORT}} \
  --deep-reasoning-effort {{DEEP_REASONING_EFFORT}} \
  --deep-phases {{DEEP_PHASES}} \
  --force
```

Then score, fill `scorecard.md`, `misses.md`, and `result-record.json`, and run:

```bash
bin/design-lab record-result \
  --round-dir design-lab/runs/{{LOOP_NAME}}/round-02 \
  --force
```

## Step 9: Repeat Up To Max Rounds

For round `N`, create the next candidate from the previous best candidate/source. If the previous best candidate was `round-02-a`, create round 3 with:

```bash
bin/design-lab create-candidate \
  --loop-name {{LOOP_NAME}} \
  --candidate round-03-a \
  --source-candidate round-02-a \
  --force
```

Run:

```bash
bin/design-lab start-round \
  --benchmark {{BENCHMARK_NAME}} \
  --candidate round-03-a \
  --loop-name {{LOOP_NAME}} \
  --round 3 \
  --max-rounds {{MAX_ROUNDS}} \
  --execute-audit \
  --parallel-jobs {{PARALLEL_JOBS}} \
  --reasoning-effort {{REASONING_EFFORT}} \
  --deep-reasoning-effort {{DEEP_REASONING_EFFORT}} \
  --deep-phases {{DEEP_PHASES}} \
  --force
```

After every round:

1. Score against ground truth.
2. Fill exact found/partial/missed result details.
3. Run `record-result`.
4. Run:

```bash
bin/design-lab leaderboard \
  --loop-name {{LOOP_NAME}}
```

If testing multiple candidates in the same numbered round, use `--trial-name` so outputs do not collide.

## Step 10: Promote Best

After stopping, run:

```bash
bin/design-lab promote-best \
  --loop-name {{LOOP_NAME}} \
  --new-design {{PROMOTED_DESIGN}} \
  --force
```

Only this best scored source/candidate should be copied into `designs/`.

## Final Response

Report:

- promoted design path,
- leaderboard path,
- best score,
- exact found findings,
- exact partial findings,
- exact missed findings,
- false positives,
- important general prompt/design changes made,
- archived candidate/result paths,
- any commands that failed or could not be run.
