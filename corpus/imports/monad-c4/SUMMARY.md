# Corpus Import Summary

- Repo: `/testing/learning/2025-09-monad`
- Source report: `/testing/learning/2025-09-monad-report.md`
- Source URL: `https://code4rena.com/reports/2025-09-monad`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/monad-c4`
- Bundle slug: `monad-c4`
- Finding count: `11`
- Included severities: `High`, `Medium`
- Excluded severities: `Low`, `Informational`
- Enrichment status: `records/cards/evals enriched in place`

## Bug Family Counts

- `input_validation_and_invariant_enforcement`: `4`
- `resource_accounting_and_limits`: `4`
- `signature_binding_and_signer_scope`: `1`
- `state_machine_and_lifecycle_consistency`: `2`

## Severity Counts

- `high`: `4`
- `medium`: `7`

## Language Counts

- `cpp`: `3`
- `rust`: `10`

## What Was Created

- `records/`: enriched YAML corpus records for each H/M finding
- `cards/root-cause/`: enriched root-cause retrieval cards
- `cards/code-shape/`: enriched code-pattern retrieval cards
- `cards/validation/`: enriched validation and false-positive caution cards
- `evals/`: eval records for detection calibration
- `raw-findings/`: split Code4rena report sections for H-01 through M-07
- `manifest.json`: machine-readable import index

## Enrichment Notes

- These are external-audit confirmed C4 High/Medium findings and are marked `tier_a_confirmed`.
- Low and informational findings were intentionally left out of this import.
- Before-code references point to `/testing/learning/2025-09-monad`; after-code references point to current upstream spot checks at the commits in `manifest.json`.
- The records are written as reusable DLT audit patterns rather than Monad-only instructions.
