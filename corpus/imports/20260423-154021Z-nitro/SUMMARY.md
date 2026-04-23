# Corpus Import Summary

- Repo: `/testing/nitro`
- Source findings: `/testing/nitro/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260423-154021Z-nitro`
- Finding count: `40`

## Bug Family Counts

- `authz_and_role_gates`: `1`
- `input_validation_and_invariant_enforcement`: `34`
- `resource_accounting_and_limits`: `1`
- `signature_binding_and_signer_scope`: `4`

## Confidence Tier Counts

- `tier_a_confirmed`: `3`
- `tier_b_likely`: `37`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Next Step

Enrich the generated stubs with stronger invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.

## Parallel Enrichment

- Worker plan: `/testing/dlt-ai-audit-system/corpus/imports/20260423-154021Z-nitro/parallel-enrichment`
- Requested worker count: `6`
- Effective worker count: `6`
- Start one worker per `worker-XX.md` file and have each worker edit only its assigned findings.
