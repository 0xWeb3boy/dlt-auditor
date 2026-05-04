# Corpus Import Summary

- Repo: `/work/stacks-core`
- Source findings: `/work/stacks-core/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/20260504-092917Z-stacks-core`
- Finding count: `28`

## Bug Family Counts

- `authz_and_role_gates`: `2`
- `input_validation_and_invariant_enforcement`: `15`
- `resource_accounting_and_limits`: `1`
- `signature_binding_and_signer_scope`: `7`
- `state_machine_and_lifecycle_consistency`: `3`

## Confidence Tier Counts

- `tier_a_confirmed`: `1`
- `tier_b_likely`: `27`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
