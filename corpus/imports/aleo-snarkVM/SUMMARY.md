# Corpus Import Summary

- Repo: `/work/snarkVM`
- Source findings: `/work/snarkVM/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/aleo-snarkVM`
- Finding count: `15`

## Bug Family Counts

- `authz_and_role_gates`: `1`
- `input_validation_and_invariant_enforcement`: `12`
- `signature_binding_and_signer_scope`: `2`

## Confidence Tier Counts

- `tier_a_confirmed`: `1`
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

- Records, root-cause cards, code-shape cards, validation cards, and evals have been enriched in place from the 15 kept validated findings.
- Bundle name: `aleo-snarkVM`
- Enrichment kept unproven exploit claims conservative and emphasized reusable audit patterns.
