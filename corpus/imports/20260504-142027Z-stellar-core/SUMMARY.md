# Corpus Import Summary

- Repo: `/work/stellar-core`
- Source findings: `/work/stellar-core/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/20260504-142027Z-stellar-core`
- Finding count: `14`

## Bug Family Counts

- `attestation_trust_and_freshness`: `1`
- `authz_and_role_gates`: `1`
- `input_validation_and_invariant_enforcement`: `11`
- `signature_binding_and_signer_scope`: `1`

## Confidence Tier Counts

- `tier_a_confirmed`: `2`
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
