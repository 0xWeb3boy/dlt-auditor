# Root-Cause Card

## Metadata

- ID: `bor-2016-11-24-bor-storage-12d654a6f`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `consensus-state-inconsistency`
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
- Secondary impact: state-integrity

## Short Reusable Lesson

- Empty-account touch behavior was not modeled as an explicit reversible journaled state transition. As a result, a revert could fail to remove account state introduced only by a touch during execution.
