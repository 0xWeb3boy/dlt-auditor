# Corpus Import Summary

- Repo: `/testing/optimism`
- Source findings: `/testing/optimism/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260424-064958Z-optimism`
- Finding count: `83`

## Bug Family Counts

- `attestation_trust_and_freshness`: `2`
- `authz_and_role_gates`: `3`
- `input_validation_and_invariant_enforcement`: `75`
- `signature_binding_and_signer_scope`: `3`

## Confidence Tier Counts

- `tier_a_confirmed`: `8`
- `tier_b_likely`: `75`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
