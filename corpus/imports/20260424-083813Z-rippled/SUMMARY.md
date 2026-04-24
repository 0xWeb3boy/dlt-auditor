# Corpus Import Summary

- Repo: `/testing/rippled`
- Source findings: `/testing/rippled/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260424-083813Z-rippled`
- Finding count: `73`

## Bug Family Counts

- `attestation_trust_and_freshness`: `2`
- `authz_and_role_gates`: `13`
- `checked_arithmetic_and_parameter_bounds`: `1`
- `input_validation_and_invariant_enforcement`: `53`
- `signature_binding_and_signer_scope`: `4`

## Confidence Tier Counts

- `tier_a_confirmed`: `11`
- `tier_b_likely`: `62`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.

## Enrichment Status

- Status: `completed`
- Enriched records: `73`
- Enriched root-cause cards: `73`
- Enriched code-shape cards: `73`
- Enriched validation cards: `73`
- Enriched evals: `73`
- Validation: record and eval YAML parsed successfully; no placeholder markers remain in generated records, cards, or evals.
