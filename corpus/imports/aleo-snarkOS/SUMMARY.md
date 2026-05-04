# Corpus Import Summary

- Repo: `/work/snarkOS`
- Source findings: `/work/snarkOS/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/aleo-snarkOS`
- Finding count: `20`

## Bug Family Counts

- `authz_and_role_gates`: `2`
- `input_validation_and_invariant_enforcement`: `16`
- `signature_binding_and_signer_scope`: `2`

## Confidence Tier Counts

- `tier_a_confirmed`: `6`
- `tier_b_likely`: `14`

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

- Enrichment completed in place for `20` records.
- Updated artifact sets: `records/`, `cards/root-cause/`, `cards/code-shape/`, `cards/validation/`, and `evals/`.
- The enriched entries include generic invariants, missing properties, trust boundaries, entrypoint types, sensitive sinks, attacker capabilities, preconditions, impact bands, severity guidance, reusable search motifs, patch patterns, and false-positive cautions.
- `manifest.json` was updated with the final bundle name and enriched index metadata.
