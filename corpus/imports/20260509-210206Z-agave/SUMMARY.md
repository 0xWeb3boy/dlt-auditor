# Corpus Import Summary

- Repo: `/testing/agave`
- Source findings: `/testing/agave/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260509-210206Z-agave`
- Finding count: `14`

## Bug Family Counts

- `authz_and_role_gates`: `1`
- `input_validation_and_invariant_enforcement`: `12`
- `signature_binding_and_signer_scope`: `1`

## Confidence Tier Counts

- `tier_a_confirmed`: `1`
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
