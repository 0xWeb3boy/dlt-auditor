# Root-Cause Card

## Metadata

- ID: `bor-2025-09-08-bor-consensus-abe386cf7`
- Bug family: `input_validation_and_invariant_enforcement`
- Bug class: `validator-set-validation`
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

- The visible root cause is under-enforced consistency checking in pre-Rio consensus handling: header validator or producer bytes were not explicitly checked in this path before seal verification, and span handling tolerated empty SelectedProducers data. The evidence does not prove whether this was exploitable or only a correctness issue.
