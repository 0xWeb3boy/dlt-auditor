# Root-Cause Card

## Metadata

- ID: `bor-2026-02-18-bor-transaction-processing-bff847a3d`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `resource-exhaustion`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `resource limit and input validity enforcement`

## Violated Invariant

- Invariant: Attacker-controlled input must be bounded and rejected before it can drive unbounded allocation, expensive processing, queue growth, or process termination.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: denial-of-service
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The background verifier built its work from the distance between a milestone boundary and the current head and materialized headers into memory before batch verification. The supplied evidence suggests that this path lacked a sufficiently explicit bounded-work control and relied on weaker configuration/startup assumptions than the patched version.
