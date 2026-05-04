# Corpus Import Summary

- Repo: `/work/zksync-era`
- Source findings: `/work/zksync-era/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/20260504-153357Z-zksync-era`
- Finding count: `7`

## Bug Family Counts

- `authz_and_role_gates`: `1`
- `input_validation_and_invariant_enforcement`: `5`
- `signature_binding_and_signer_scope`: `1`

## Confidence Tier Counts

- `tier_a_confirmed`: `1`
- `tier_b_likely`: `6`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
