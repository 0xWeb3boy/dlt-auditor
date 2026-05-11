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

To render a filled prompt:

```bash
/testing/dlt-ai-audit-system/bin/design-lab learning-loop-prompt \
  --repo /path/to/competition/repo \
  --findings /path/to/known/findings.md \
  --benchmark contest-name
```

Then paste the rendered prompt into Codex.
