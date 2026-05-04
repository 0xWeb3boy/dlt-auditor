# Validation Card

## Metadata

- ID: `thor-2026-01-07-thor-core-logic-318fdccd`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-request-criteria-hardening`

## What Confirmed The Issue

- handleFilterTransferLogs now rejects len(CriteriaSet) greater than maxCriteriaCount.
- Logdb event and transfer queries now use prepared/cached statements.
- Phase 4 kept the finding as likely `security-hardening`, not as a confirmed vulnerability.

## What Could Have Invalidated It

- Another layer already enforced the same maximum criteria count.
- The criteria list cannot affect query complexity or allocation.
- The endpoint is not exposed to untrusted clients.

## Severity Guidance

- Expected impact band: low node-local availability hardening
- Expected severity band: `medium_or_low`
- Rationale: This is likely resource-control hardening for an API query path. The blast radius is node/API availability, and the evidence does not prove an exploitable denial of service.

## False-Positive Cautions

- No issue if a lower layer caps criteria count or query cost.
- No issue if the endpoint is private and rate-limited for trusted callers.
- Prepared-statement caching alone is not proof of injection or DoS.
