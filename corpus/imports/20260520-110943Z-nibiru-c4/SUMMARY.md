# Corpus Import Summary

- Repo: `/testing/learning-nibiru/2024-11-nibiru`
- Source report: `/testing/learning-nibiru/report.md`
- Bundle root: `/testing/dlt-ai-audit-system/corpus/imports/20260520-110943Z-nibiru-c4`
- Corpus slug: `nibiru-c4`
- Contest start: `2024-11-12`
- Contest end: `2024-11-26`
- Finding count: `21`
- Excluded: Low, QA, and non-critical findings

## Included Sources

- 6 High-risk main C4 findings
- 10 Medium-risk main C4 findings
- 3 High-severity mitigation-review findings
- 2 Medium-severity mitigation-review findings

## Severity Counts

- `high`: `9`
- `medium`: `12`

## Bug Family Counts

- `attestation_trust_and_freshness`: `2`
- `checked_arithmetic_and_parameter_bounds`: `1`
- `input_validation_and_invariant_enforcement`: `2`
- `resource_accounting_and_limits`: `8`
- `state_machine_and_lifecycle_consistency`: `8`

## Confidence Tier Counts

- `tier_a_confirmed`: `15`
- `tier_b_likely`: `6`

## Post-Contest Fix Evidence

- PR metadata was checked against `NibiruChain/nibiru` for the listed mitigation PRs.
- Exact PR created/merged timestamps are recorded in each record's `notes`.
- M-09 and M-10 have report-linked mitigations merged on the contest end date, `2024-11-26`; the other report-linked mitigation PRs are after that date.
- Findings without a confirmed mitigation PR in the report are marked as public report findings or acknowledged risks rather than confirmed security fixes.

## What Was Created

- `records/`: normalized YAML records for each finding
- `cards/root-cause/`: root-cause retrieval cards
- `cards/code-shape/`: code-pattern retrieval cards
- `cards/validation/`: validation and false-positive caution cards
- `evals/`: eval records
- `raw-findings/`: source report sections split by finding
- `manifest.json`: machine-readable import index
