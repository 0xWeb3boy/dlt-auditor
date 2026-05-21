# Corpus Import Summary

- Project: `blast`
- Source report: `/testing/dlt-ai-audit-system/design-lab/benchmarks/blast/ground-truth/report.md`
- Competition window: `2024-01-31` to `2024-02-21`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260521-085441Z-blast`
- Finding count: `28`

## Bug Family Counts

- `attestation_trust_and_freshness`: `1`
- `authz_and_role_gates`: `1`
- `input_validation_and_invariant_enforcement`: `1`
- `resource_accounting_and_limits`: `14`
- `staking_registry_and_accountability`: `1`
- `state_machine_and_lifecycle_consistency`: `10`

## Severity Counts

- `high`: `8`
- `medium`: `20`

## What Was Created

- `records/`: enriched normalized YAML records
- `cards/root-cause/`: conceptual retrieval cards
- `cards/code-shape/`: code-search retrieval cards
- `cards/validation/`: confirmation and false-positive caution cards
- `evals/`: expected detector-output records
- `raw-findings/`: report-derived per-finding source summaries
- `manifest.json`: machine-readable import index

## Notes

- Patch patterns are derived from the report recommendations and reusable fix shape.
- This bundle intentionally avoids embedding long verbatim report sections; raw findings are concise source summaries.
