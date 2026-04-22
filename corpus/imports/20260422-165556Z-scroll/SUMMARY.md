# Corpus Import Summary

- Repo: `/testing/scroll`
- Source findings: `/testing/scroll/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260422-165556Z-scroll`
- Finding count: `14`

## Bug Family Counts

- `authz_and_role_gates`: `1`
- `input_validation_and_invariant_enforcement`: `12`
- `signature_binding_and_signer_scope`: `1`

## Confidence Tier Counts

- `tier_a_confirmed`: `2`
- `tier_b_likely`: `12`

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

- Worker plan: `/testing/dlt-ai-audit-system/corpus/imports/20260422-165556Z-scroll/parallel-enrichment`
- Requested worker count: `6`
- Effective worker count: `6`
- Start one worker per `worker-XX.md` file and have each worker edit only its assigned findings.
