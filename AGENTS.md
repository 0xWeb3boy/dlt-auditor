# DLT AI Audit System Instructions

If the user asks to "run learning loop from dlt-ai-audit-system on this codebase", use:

```text
design-lab/prompts/run-learning-loop.md
```

Ask for the known findings file/directory if it was not provided. If the target repo is unclear, ask for it; if the user says "this codebase", use the current repository unless the current repository is `dlt-ai-audit-system`.

Keep the blind audit separated from ground truth. Store experimental candidates and exact results under `design-lab/runs/<loop>/`, and promote only the best scored candidate/source into `designs/`.
