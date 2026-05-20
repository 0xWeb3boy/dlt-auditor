# Root-Cause Card

## Metadata

- ID: `nibiru-c4-2024-11-m06-tracetx-unbounded-predecessors`
- Bug family: `resource_accounting_and_limits`
- Bug class: `unbounded-rpc-simulation-work`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `rpc workload limits`

## Violated Invariant

- Invariant: Read-only trace endpoints must bound predecessor count, gas, and wall-clock time for caller-supplied simulation workloads.

## Trust Boundary

- Boundary: rpc-client->node tracing service

## Attack Surface

- Entrypoint type: gRPC TraceTx query
- Sensitive sink: loop that simulates req.Predecessors with effectively caller-chosen workload

## Impact Pattern

- Primary impact: RPC resource exhaustion
- Secondary impact: public endpoint availability loss

## Short Reusable Lesson

- TraceTx iterated over caller-supplied predecessor transactions and simulated each before tracing the target message without an explicit global bound.
