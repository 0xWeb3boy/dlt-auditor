# Run Learning Loop

When you want a Codex session to run the eval-driven learning loop, use the canonical prompt:

```text
design-lab/prompts/run-learning-loop.md
```

Shortcut phrase for future sessions:

```text
run learning loop from dlt-ai-audit-system on this codebase
```

The session still needs the known findings path. If the target repo is not obvious, provide that too.

Blind audit guardrail: the audit workers must not read `design-lab/benchmarks/**`, benchmark `ground-truth/**`, or prior learning-loop artifacts under `design-lab/runs/**`. Ground truth and prior results are only for scoring/refinement after the blind audit completes.

Limit-resume guardrail: if Codex limits are exhausted during a round, do not rerun `start-round --force`. Resume the same round with `bin/design-lab resume-audit --round-dir design-lab/runs/<loop>/round-XX`.

Speed/reasoning default: learning-loop audits run Codex service tier `standard`, discovery phases at `high`, and deep judgment phases at `xhigh`. The prompt renderer exposes `--service-tier`, `--reasoning-effort`, `--deep-reasoning-effort`, and `--deep-phases` if you want a different split.

To render a filled prompt:

```bash
/testing/dlt-ai-audit-system/bin/design-lab learning-loop-prompt \
  --repo /path/to/competition/repo \
  --findings /path/to/known/findings.md \
  --benchmark contest-name
```

Then paste the rendered prompt into Codex.
