# Corpus Import Summary

- Repo: `/testing/bor`
- Source findings: `/testing/bor/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260424-064909Z-bor`
- Finding count: `75`

## Bug Family Counts

- `checked_arithmetic_and_parameter_bounds`: `2`
- `input_validation_and_invariant_enforcement`: `68`
- `resource_accounting_and_limits`: `1`
- `signature_binding_and_signer_scope`: `4`

## Confidence Tier Counts

- `tier_a_confirmed`: `9`
- `tier_b_likely`: `66`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
