# Validation Card

## Metadata

- ID: `fuel-core-2025-09-15-fuel-core-transaction-processing-d526593aff`
- Bug family: `resource_accounting_and_limits`
- Bug class: `graphql-query-complexity-accounting-hardening`
- Security verdict: `likely`
- Validated as: `security-hardening`

## What Confirmed The Issue

- Patch changes transaction and message query formulas to first * (child_complexity + storage_read).
- Patch increases several default GraphQL query cost constants.

## What Could Have Invalidated It

- An upstream gateway enforces strict rate and page-size limits independent of complexity.
- The changed fields are unavailable to untrusted clients.

## Severity Guidance

- Expected impact band: `medium`
- Expected severity band: `medium`
- Rationale: Undercharging paginated queries can allow more storage reads than the configured budget intended. Evidence supports hardening, not a proven outage.

## False-Positive Cautions

- No issue if maximum page size is tiny and separately enforced.
- No issue if the resolver performs constant-time indexed reads regardless of requested item count.
