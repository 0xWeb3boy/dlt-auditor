# Corpus Import Summary

- Repo: `/testing/go-ethereum`
- Source findings: `/testing/go-ethereum/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260424-114423Z-geth-arb`
- Bundle slug: `geth-arb`
- Finding count: `38`
- Enrichment status: `records/cards/evals enriched in place`

## Bug Family Counts

- `authz_and_role_gates`: `4`
- `input_validation_and_invariant_enforcement`: `12`
- `resource_accounting_and_limits`: `8`
- `signature_binding_and_signer_scope`: `6`
- `state_machine_and_lifecycle_consistency`: `8`

## Confidence Tier Counts

- `tier_a_confirmed`: `13`
- `tier_b_likely`: `25`

## What Was Created

- `records/`: enriched YAML corpus records for each kept finding
- `cards/root-cause/`: enriched root-cause retrieval cards
- `cards/code-shape/`: enriched reusable code-pattern retrieval cards
- `cards/validation/`: enriched validation and false-positive caution cards
- `evals/`: enriched eval records
- `raw-findings/`: copied phase-4 kept finding markdown
- `manifest.json`: machine-readable import index

## Enrichment Notes

- Enrichment was derived from the validated finding text and conservative phase-4 verdicts.
- Confirmed cases can be used as eval positives; likely hardening cases are retrieval examples unless separate exploit evidence is added.
- Claims are intentionally generic enough to transfer to other blockchain/DLT repositories.
