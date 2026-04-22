# Corpus Import Summary

- Repo: `/testing/oasis-core`
- Source findings: `/testing/oasis-core/validated-findings/kept`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260422-155646Z-oasis-core`
- Finding count: `48`

## Bug Family Counts

- `attestation_trust_and_freshness`: `8`
- `authz_and_role_gates`: `9`
- `checked_arithmetic_and_parameter_bounds`: `2`
- `input_validation_and_invariant_enforcement`: `8`
- `resource_accounting_and_limits`: `5`
- `signature_binding_and_signer_scope`: `5`
- `staking_registry_and_accountability`: `7`
- `state_machine_and_lifecycle_consistency`: `4`

## Confidence Tier Counts

- `tier_a_confirmed`: `8`
- `tier_b_likely`: `40`

## What Was Created

- `records/`: normalized YAML stubs for each finding
- `cards/root-cause/`: short root-cause retrieval cards
- `cards/code-shape/`: short code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval record stubs
- `manifest.json`: machine-readable import index

## Enrichment Status

- Status: `completed`
- Enriched outputs:
  - `48` records
  - `48` root-cause cards
  - `48` code-shape cards
  - `48` validation cards
  - `48` evals

The generated stubs in this bundle have already been enriched with normalized invariants, trust boundaries, impact details, search motifs, patch patterns, and false-positive cautions.

## Parallel Enrichment

- Worker plan: `/testing/dlt-ai-audit-system/corpus/imports/20260422-155646Z-oasis-core/parallel-enrichment`
- Requested worker count: `6`
- Effective worker count: `6`
- Start one worker per `worker-XX.md` file and have each worker edit only its assigned findings.
