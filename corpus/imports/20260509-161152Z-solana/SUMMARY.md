# Corpus Import Summary

- Repo: `/testing/solana`
- Source findings: `/testing/solana/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260509-161152Z-solana`
- Finding count: `139`

## Bug Family Counts

- `attestation_trust_and_freshness`: `5`
- `authz_and_role_gates`: `14`
- `checked_arithmetic_and_parameter_bounds`: `5`
- `input_validation_and_invariant_enforcement`: `97`
- `resource_accounting_and_limits`: `4`
- `signature_binding_and_signer_scope`: `9`
- `staking_registry_and_accountability`: `3`
- `state_machine_and_lifecycle_consistency`: `2`

## Confidence Tier Counts

- `tier_a_confirmed`: `25`
- `tier_b_likely`: `114`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.

## Enrichment Completed

- Enriched in place on 2026-05-09.
- Updated `139` normalized records.
- Updated `139` root-cause cards.
- Updated `139` code-shape cards.
- Updated `139` validation cards.
- Updated `139` eval records.
- Enrichment source material: raw finding frontmatter, summary, root-cause, fix-pattern, evidence, and validation sections.
- Family labels were restored from `manifest.json`; missing properties, trust boundaries, sinks, impact bands, search motifs, patch patterns, and false-positive cautions were filled from the raw finding content.
