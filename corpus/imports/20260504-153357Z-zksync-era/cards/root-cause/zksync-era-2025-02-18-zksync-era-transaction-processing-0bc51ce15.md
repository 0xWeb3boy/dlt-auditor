# Root-Cause Card

## Metadata

- ID: `zksync-era-2025-02-18-zksync-era-transaction-processing-0bc51ce15`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `migration-state-guard`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `migration-state-gating`

## Violated Invariant

- Invariant: Protocol transition code must refresh and enforce migration state before routing events or performing state-advancing operations.

## Trust Boundary

- Boundary: Observed L1 or settlement-layer migration state crosses into local event routing and batch commit aggregation.

## Attack Surface

- Entrypoint type: Background event watcher and transaction aggregation loop.
- Sensitive sink: Batch commit aggregation and settlement-layer event processing during gateway migration.

## Impact Pattern

- Primary impact: Protocol-state consistency during migration.
- Secondary impact: Reduced risk of unsafe state-advancing operations while a transition is active.

## Short Reusable Lesson

- State-machine transitions need guards close to each sensitive action. Refresh transition state before event routing or aggregation, and block operations that are unsafe in the active phase.
