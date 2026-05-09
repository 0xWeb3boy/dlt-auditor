# Corpus Import Summary

- Repo: `/testing/nibiru`
- Source findings: `/testing/nibiru/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260509-213214Z-nibiru`
- Finding count: `15`

## Bug Family Counts

- `authz_and_role_gates`: `2`
- `input_validation_and_invariant_enforcement`: `10`
- `resource_accounting_and_limits`: `3`

## Confidence Tier Counts

- `tier_a_confirmed`: `2`
- `tier_b_likely`: `13`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
