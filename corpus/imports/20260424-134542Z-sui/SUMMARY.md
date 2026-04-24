# Corpus Import Summary

- Repo: `/testing/sui`
- Source findings: `/testing/sui/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260424-134542Z-sui`
- Finding count: `68`

## Bug Family Counts

- `authz_and_role_gates`: `3`
- `checked_arithmetic_and_parameter_bounds`: `2`
- `input_validation_and_invariant_enforcement`: `54`
- `resource_accounting_and_limits`: `2`
- `signature_binding_and_signer_scope`: `7`

## Confidence Tier Counts

- `tier_a_confirmed`: `8`
- `tier_b_likely`: `60`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
