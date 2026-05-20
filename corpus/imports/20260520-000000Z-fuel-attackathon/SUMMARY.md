# Corpus Import Summary

- Project: `fuel-attackathon`
- Source findings: `/testing/learning_2/fuel-network-attackathon-findings.md`
- Source index: <https://reports.immunefi.com/fuel-network-or-attackathon>
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260520-000000Z-fuel-attackathon`
- Attackathon date: `2024-06-17`
- Finding count: `36`
- Excluded severities: `Low`, `Insight`

## Bug Family Counts

- `authz_and_role_gates`: `2`
- `checked_arithmetic_and_parameter_bounds`: `17`
- `input_validation_and_invariant_enforcement`: `12`
- `resource_accounting_and_limits`: `2`
- `state_machine_and_lifecycle_consistency`: `3`

## Confidence Tier Counts

- `tier_a_confirmed`: `14`
- `tier_b_likely`: `22`

## Severity Counts

- `critical`: `3`
- `high`: `16`
- `medium`: `17`

## What Was Created

- `raw-findings/`: one split markdown source file per included report
- `records/`: enriched normalized YAML records
- `cards/root-cause/`: root-cause retrieval cards
- `cards/code-shape/`: code-shape retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval records
- `manifest.json`: machine-readable import index

## Notes

- Report `32965` overlaps an existing Fuel Core corpus pattern but is retained under `fuel-attackathon` provenance.
- Patch patterns are normalized from public report descriptions and current corpus conventions; this import does not claim every current upstream fix was independently re-verified.
