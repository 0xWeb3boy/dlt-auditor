# Root-Cause Card

## Metadata

- ID: `snarkvm-2025-03-05-snarkvm-consensus-204e8b564`
- Bug family: `resource_accounting_and_limits`
- Bug class: `recursion-resource-accounting-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `recursive-call-bound`

## Violated Invariant

- Invariant: Execution cost and recursion limits must be computed from the current call graph and validated before a program stack is accepted.

## Trust Boundary

- Boundary: program call graph -> stack initialization and fee/resource accounting

## Attack Surface

- Entrypoint type: deployment-or-stack-initialization
- Sensitive sink: recursive call expansion and finalize cost calculation

## Impact Pattern

- Primary impact: resource accounting and liveness hardening
- Secondary impact: fee consistency for recursive program execution

## Short Reusable Lesson

- Resource limits over program graphs should be checked against the graph being accepted, not against stale metadata.
