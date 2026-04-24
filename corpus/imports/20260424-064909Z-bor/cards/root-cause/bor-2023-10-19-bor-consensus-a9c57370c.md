# Root-Cause Card

## Metadata

- ID: `bor-2023-10-19-bor-consensus-a9c57370c`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-safety`
- Confidence tier: `tier_b_likely`

## Missing Property

- Missing property: `consensus invariant enforcement`

## Violated Invariant

- Invariant: Consensus-critical data must satisfy the same validation rules on every node before it can influence state transition, fork choice, rewards, or canonical-chain decisions.

## Trust Boundary

- Boundary: untrusted block, header, transaction, or state data to consensus engine boundary

## Attack Surface

- Entrypoint type: block/header/transaction validation or state-transition path
- Sensitive sink: canonical chain selection, state root commitment, or consensus state mutation

## Impact Pattern

- Primary impact: consensus-instability
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The fork-choice implementation allowed an equal-TD, equal-height tie to be resolved by local randomness instead of a deterministic rule derived from the competing headers.
