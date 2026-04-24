# Root-Cause Card

## Metadata

- ID: `geth-arb-2018-09-20-go-ethereum-storage-d6254f827b`
- Bug family: `state_machine_and_lifecycle_consistency`
- Bug class: `fork-choice-tie-break-hardening`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `deterministic-fork-choice`

## Violated Invariant

- Invariant: Fork-choice tie breaks should be deterministic and preference-preserving so equal-work alternatives cannot induce unnecessary local reorg churn.

## Trust Boundary

- Boundary: competing peer-supplied chain head -> local canonical chain selection

## Attack Surface

- Entrypoint type: block import and reorg decision path
- Sensitive sink: canonical-chain selection and reorg execution

## Impact Pattern

- Primary impact: consensus-stability
- Secondary impact: reorg-resistance
- Severity guide: low-medium

## Short Reusable Lesson

- Equal-difficulty same-height blocks could trigger random reorg behavior instead of preferentially retaining the local canonical block. Replace random tie-breaking with deterministic local-chain preference when total difficulty and height are equal.
