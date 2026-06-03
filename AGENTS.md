# DLT Auditor Instructions

This repository is the runtime-focused sibling of `dlt-ai-audit-system`.

Use it to run stable audit designs from `designs/` against target codebases. Do not add back the learning loop, benchmark ground truth, candidate scoring, scorecards, miss analysis, leaderboards, or promotion workflows unless the user explicitly asks to rebuild that separate system.

For one design, scaffold with:

```text
bin/run-design <design-name> /path/to/target-repo --run-name <run-name> --parallel-jobs 8
```

Then execute the generated design run with that design's `bin/run-parallel-codex`. Use `--agent claude` when the user asks for Claude Code instead of Codex.

For multiple designs, use:

```text
bin/run-blind-suite --repo /path/to/target-repo --suite-name <suite-name> --design <design-name> --parallel-jobs 8
```

Blind suite outputs live under `runs/<suite-name>/`. If worker limits are exhausted, preserve the suite and resume it with:

```text
bin/run-blind-suite --suite-name <suite-name> --resume
```

Keep blind audit execution separated from answer-key material. During blind audit execution, do not read known findings, benchmark ground truth, scorecards, miss analyses, result records, leaderboards, refinement plans, audit-output snapshots, candidate result archives, prior round folders, sibling suite outputs, or stable `designs/*/runs/**` output.

Default blind execution uses Codex service tier `standard`, reasoning `high` for discovery phases, and reasoning `xhigh` for `canonicalize`, `validations`, `aggregate`, and `final` unless the user asks for a different split. For Claude Code, use `--agent claude` and do not pass Codex reasoning or service-tier overrides.
