# Corpus Import Summary

- Repo: `/work/moonbeam`
- Source findings: `/work/moonbeam/validated-findings/kept`
- Bundle root: `/work/dlt-ai-audit-system/corpus/imports/20260504-114816Z-moonbeam`
- Finding count: `19`
- Enrichment status: `completed`

## Bug Family Counts

- `authz_and_role_gates`: `6`
- `input_validation_and_invariant_enforcement`: `7`
- `resource_accounting_and_limits`: `3`
- `signature_binding_and_signer_scope`: `3`

## Confidence Tier Counts

- `tier_a_confirmed`: `6`
- `tier_b_likely`: `13`

## Validated Type Counts

- `security-fix`: `5`
- `security-hardening`: `14`

## Severity Guess Counts

- `high`: `8`
- `medium`: `11`

## What Was Created

- `records/`: enriched YAML records for each kept finding
- `cards/root-cause/`: enriched root-cause retrieval cards
- `cards/code-shape/`: enriched code-pattern retrieval cards
- `cards/validation/`: enriched validation and false-positive caution cards
- `evals/`: enriched eval records
- `raw-findings/`: copied validated source findings
- `manifest.json`: machine-readable import index from bundle creation

## Enrichment Notes

- Invariants, trust boundaries, attacker capabilities, preconditions, impact bands, severity guesses, search motifs, patch patterns, and false-positive cautions were filled in place.
- Confirmed findings retain `tier_a_confirmed`; likely hardening/fix cases retain `tier_b_likely` and conservative severity language.
- No raw finding text was copied wholesale into the enriched artifacts.
