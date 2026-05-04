# Corpus Import Summary

- Repo: `/work/fuel-core`
- Source findings: `/work/fuel-core/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/20260504-105708Z-fuel-core`
- Finding count: `15`

## Bug Family Counts

- `input_validation_and_invariant_enforcement`: `10`
- `resource_accounting_and_limits`: `2`
- `signature_binding_and_signer_scope`: `2`
- `state_machine_and_lifecycle_consistency`: `1`

## Confidence Tier Counts

- `tier_a_confirmed`: `3`
- `tier_b_likely`: `12`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
