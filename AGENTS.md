# DLT AI Audit System Instructions

If the user asks to "run learning loop from dlt-ai-audit-system on this codebase", use:

```text
design-lab/prompts/run-learning-loop.md
```

Ask for the known findings file/directory if it was not provided. If the target repo is unclear, ask for it; if the user says "this codebase", use the current repository unless the current repository is `dlt-ai-audit-system`.

Keep the blind audit separated from ground truth. During blind audit execution, do not read `design-lab/benchmarks/**`, benchmark `ground-truth/**`, or previous learning-loop artifacts under `design-lab/runs/**` such as `scorecard.md`, `misses.md`, `result-record.json`, `design-refinement-plan.md`, `leaderboard.md`, `audit-output-snapshot/**`, candidate `results/**`, or prior round folders.

If the active candidate design lives under `design-lab/runs/<loop>/candidates/<candidate>/design/`, that candidate's own design files and generated audit run directory are allowed. Other loop/scoring/refinement artifacts remain forbidden.

Store experimental candidates and exact results under `design-lab/runs/<loop>/`, and promote only the best scored candidate/source into `designs/`.

When executing learning-loop audits, use Codex service tier `standard`, reasoning `high` for discovery phases, and reasoning `xhigh` for canonicalize, validations, aggregate, and final phases unless the user asks for a different split.

If Codex limits are exhausted during a learning-loop audit, preserve the round and resume it later with `bin/design-lab resume-audit --round-dir design-lab/runs/<loop>/round-XX`. Do not recreate the same round with `start-round --force` unless the user explicitly wants to discard the interrupted run.
