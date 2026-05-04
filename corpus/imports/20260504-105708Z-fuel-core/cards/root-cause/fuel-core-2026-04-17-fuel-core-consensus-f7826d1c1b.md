# Root-Cause Card

## Metadata

- ID: `fuel-core-2026-04-17-fuel-core-consensus-f7826d1c1b`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `consensus-liveness`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `identity-normalization`

## Violated Invariant

- Reconciliation votes for the same committed block must be grouped by canonical block identity, while volatile metadata may only break ties.

## Trust Boundary

- Boundary: `durable-consensus-store->leader-reconciliation`
- Entrypoint type: `state-transition`
- Sensitive sink: `block vote grouping and leader progress decision`

## Attack Surface

- Create or encounter inconsistent metadata for the same block across replicated backend nodes.
- Rely on reconciliation failing to reach a quorum despite matching block ids.

## Exploit Preconditions

- The same block can be stored with different epoch metadata on different Redis nodes.
- Vote grouping keys include epoch alongside block id.

## Impact Pattern

- Primary impact: `denial-of-service`
- Secondary impact: `consensus-liveness`
- Blast radius: `chain-wide`
- Severity guess: `medium`

## Short Reusable Lesson

- Consensus reconciliation should key quorum decisions on canonical identity, not incidental metadata that may diverge across replicas.
