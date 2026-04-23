# Corpus Import Summary

- Repo: `/testing/go-ethereum`
- Source findings: `/testing/go-ethereum/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260423-205007Z-go-ethereum`
- Finding count: `31`

## Bug Family Counts

- `authz_and_role_gates`: `2`
- `input_validation_and_invariant_enforcement`: `26`
- `resource_accounting_and_limits`: `1`
- `signature_binding_and_signer_scope`: `2`

## Confidence Tier Counts

- `tier_a_confirmed`: `12`
- `tier_b_likely`: `19`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
