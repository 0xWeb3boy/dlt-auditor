# Root-Cause Card

## Metadata

- ID: `thor-2024-08-22-thor-transaction-processing-f1aa5ae7`
- Bug family: `authz_and_role_gates`
- Bug class: `debug-api-tracer-allowlist-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `policy-gating`

## Violated Invariant

- Invariant: Debug tracing endpoints must instantiate only explicitly enabled tracers, and disabled-by-default deployments must reject blank, unknown, or custom tracer names before tracer construction.

## Trust Boundary

- Boundary: `rpc-client->debug-api-tracer-factory`

## Attack Surface

- Entrypoint type: `rpc-debug-handler`
- Sensitive sink: tracer instantiation, including registered tracers and optional custom JavaScript tracer creation
- Attacker capability: Send a debug trace request to an enabled API endpoint.
- Preconditions: The debug API is reachable to the caller.

## Impact Pattern

- Primary impact: debug API attack-surface reduction
- Secondary impact: node-local resource or introspection abuse
- Blast radius: `node-local`

## Short Reusable Lesson

- Administrative/debug plugin factories should be deny-by-default at the API boundary; caller-provided plugin names should be checked against explicit policy before any plugin or script construction.
