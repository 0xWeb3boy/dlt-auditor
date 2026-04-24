# Corpus Import Summary

- Repo: `/testing/sei-chain`
- Source findings: `/testing/sei-chain/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260424-143008Z-sei-chain`
- Finding count: `40`

## Bug Family Counts

- `authz_and_role_gates`: `2`
- `input_validation_and_invariant_enforcement`: `33`
- `resource_accounting_and_limits`: `1`
- `signature_binding_and_signer_scope`: `3`
- `staking_registry_and_accountability`: `1`

## Confidence Tier Counts

- `tier_a_confirmed`: `2`
- `tier_b_likely`: `38`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
