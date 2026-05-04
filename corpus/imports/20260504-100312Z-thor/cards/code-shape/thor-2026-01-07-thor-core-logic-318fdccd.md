# Code-Shape Card

## Metadata

- ID: `thor-2026-01-07-thor-core-logic-318fdccd`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-request-criteria-hardening`

## Code Shape Summary

- A transfer log filter handler validated options and nil criteria but lacked a visible maximum criteria-count check before log database querying; the fix rejects excessive criteria and routes query execution through cached prepared statements.

## Search Motifs

- filter.CriteriaSet length used to build DB query
- API validates range but not number of filter clauses
- caller-controlled list of query predicates has no max count
- log query prepares statements for unbounded dynamic criteria

## Typical Asymmetry

- The external or cross-context input is treated as already safe, while the later privileged sink assumes that admission, domain, or cardinality checks already happened upstream.

## Patch Pattern

- Add an API-level maxCriteriaCount guard before database work and use a statement cache for repeated event/transfer query execution.

## False Match Warnings

- No issue if a lower layer caps criteria count or query cost.
- No issue if the endpoint is private and rate-limited for trusted callers.
- Prepared-statement caching alone is not proof of injection or DoS.
