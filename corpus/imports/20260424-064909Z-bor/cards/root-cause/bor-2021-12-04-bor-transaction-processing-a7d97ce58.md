# Root-Cause Card

## Metadata

- ID: `bor-2021-12-04-bor-transaction-processing-a7d97ce58`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `improper-consensus-state-transition`
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

- Primary impact: consensus-integrity
- Secondary impact: medium severity conditions

## Short Reusable Lesson

- The observed root cause is incomplete wiring of genesis-related state-change logic into the finalization paths, plus missing upfront validation for loosely typed genesis allocation config data.
