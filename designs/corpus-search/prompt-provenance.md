# Prompt Provenance

This document is intentionally separate from the operational prompts.

Its purpose is to preserve where the prompt taxonomy came from without anchoring the agent during normal use.

## Why This Exists

The prompt families in `prompts/` were derived from recurring validated bug patterns observed in the source corpus for this repository.

That provenance can be useful for:

- checking that the taxonomy covers real security issues,
- explaining why certain bug families got their own prompts,
- and tuning the system over time.

It is not required for runtime use.

The agent should be able to operate correctly with only:

- `00_protocol_mapper.md`
- `01_base_hunter.md`
- `02_validation_and_impact.md`
- the generic prompt family files in `prompts/`

## Reference Map

For the detailed source-corpus mapping from validated findings to prompt families, see [finding-to-prompt-map.md](/testing/dlt-ai-audit-system/finding-to-prompt-map.md).

That file is retained as a calibration artifact, not as an operational dependency.
