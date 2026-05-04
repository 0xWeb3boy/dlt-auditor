# Root-Cause Card

## Metadata

- ID: `fuel-core-2024-07-03-fuel-core-storage-4a3cfc8e4a`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `stale-consensus-parameter-validation`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `freshness`

## Violated Invariant

- Cached validation results must be bound to the exact consensus-parameter version used to produce them and must be revalidated before inclusion under newer rules.

## Trust Boundary

- Boundary: `txpool-cache->executor-state-transition`
- Entrypoint type: `state-transition`
- Sensitive sink: `block transaction inclusion under active consensus parameters`

## Attack Surface

- Submit a transaction that validates under one parameter version but should fail or differ under a later version.
- Keep the transaction cached across a parameter upgrade.

## Exploit Preconditions

- Txpool stores checked transactions without the parameter version.
- Executor trusts cached checked transactions during block production.

## Impact Pattern

- Primary impact: `consensus-integrity`
- Secondary impact: `state-integrity`
- Blast radius: `chain-wide`
- Severity guess: `high`

## Short Reusable Lesson

- Validation caches need explicit rule-version binding whenever protocol parameters can change independently of cached objects.
