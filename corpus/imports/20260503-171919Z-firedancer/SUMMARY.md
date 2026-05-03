# Corpus Import Summary

- Repo: `/work/firedancer`
- Source findings: `/work/firedancer/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/20260503-171919Z-firedancer`
- Finding count: `38`

## Bug Family Counts

- `authz_and_role_gates`: `2`
- `checked_arithmetic_and_parameter_bounds`: `5`
- `input_validation_and_invariant_enforcement`: `31`

## Confidence Tier Counts

- `tier_a_confirmed`: `9`
- `tier_b_likely`: `29`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
