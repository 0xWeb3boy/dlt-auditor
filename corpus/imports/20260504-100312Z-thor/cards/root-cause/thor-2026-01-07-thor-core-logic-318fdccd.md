# Root-Cause Card

## Metadata

- ID: `thor-2026-01-07-thor-core-logic-318fdccd`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-request-criteria-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `request-cardinality-limit`

## Violated Invariant

- Invariant: Public query APIs must bound caller-controlled filter cardinality before translating filters into database work.

## Trust Boundary

- Boundary: `api-client->log-query-database`

## Attack Surface

- Entrypoint type: `http-filter-query-handler`
- Sensitive sink: event/transfer log database query planning and statement execution
- Attacker capability: Send API filter requests with many criteria entries.
- Preconditions: The API endpoint is reachable.

## Impact Pattern

- Primary impact: node/API resource exhaustion
- Secondary impact: query latency amplification
- Blast radius: `node-local`

## Short Reusable Lesson

- Filter APIs should enforce cardinality and cost limits at the request boundary, before caller-controlled predicates are expanded into database queries.
