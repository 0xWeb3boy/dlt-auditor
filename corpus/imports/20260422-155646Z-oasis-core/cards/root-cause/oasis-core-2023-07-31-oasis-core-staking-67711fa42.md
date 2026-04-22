# Root-Cause Card

## Metadata

- ID: `oasis-core-2023-07-31-oasis-core-staking-67711fa42`
- Bug family: `staking_registry_and_accountability`
- Bug class: `proposer-liveness-accounting-gap`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `liveness-accounting`

## Violated Invariant

- Invariant: If proposer liveness is evaluated, proposer timeout events must be attributed to the intended committee member so later liveness processing uses consistent per-member statistics.

## Trust Boundary

- Boundary: `validator->consensus`

## Attack Surface

- Entrypoint type: `state-transition`
- Sensitive sink: `validator penalty state`

## Impact Pattern

- Primary impact: `availability`
- Secondary impact: `penalty-bypass`

## Short Reusable Lesson

- If proposer liveness is evaluated, proposer timeout events must be attributed to the intended committee member so later liveness processing uses consistent per-member statistics. In this pattern, the evidence shows a liveness-accounting gap in the displayed code paths: proposer timeout handling did not record a missed proposal there, and there was no helper for resolving the selected scheduler directly into committee-member index space. However, the evidence does not prove that this caused an exploitable bypass, mis-slashing, or consensus failure before the patch. The robust fix is to make the privileged sink consume the canonical identity, state coordinate, or accounting result directly and to fail closed when that binding is missing.
