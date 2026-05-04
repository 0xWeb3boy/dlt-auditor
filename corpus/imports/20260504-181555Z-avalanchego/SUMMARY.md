# Corpus Import Summary

- Repo: `/work/avalanchego`
- Source findings: `/work/avalanchego/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/20260504-181555Z-avalanchego`
- Finding count: `17`

## Bug Family Counts

- `authz_and_role_gates`: `1`
- `checked_arithmetic_and_parameter_bounds`: `2`
- `input_validation_and_invariant_enforcement`: `13`
- `signature_binding_and_signer_scope`: `1`

## Confidence Tier Counts

- `tier_a_confirmed`: `1`
- `tier_b_likely`: `16`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.
